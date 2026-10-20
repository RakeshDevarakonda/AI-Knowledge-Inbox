import re
from typing import List, Dict, Any
from ai_knowledge_inbox.services.embedding import get_embedding, get_gemini_client
from ai_knowledge_inbox.storage import store
from ai_knowledge_inbox.config import logger

def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Computes cosine similarity between two 768-dimensional vectors."""
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = sum(a * a for a in vec_a) ** 0.5
    norm_b = sum(b * b for b in vec_b) ** 0.5

    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)


def _extract_extractive_answer(question: str, top_matches: List[Dict[str, Any]]) -> str:
    """
    Intelligent extractive fallback that extracts the most relevant sentence 
    from top chunks if the cloud LLM is offline, unauthenticated, or rate-limited.
    """
    if not top_matches:
        return "I couldn't find the answer in your saved inbox."

    q_words = set(re.findall(r"\w+", question.lower()))
    candidate_sentences = []

    for match in top_matches:
        chunk_text = match["chunk"]["text"]
        sentences = [s.strip() for s in re.split(r"[.\n!]", chunk_text) if len(s.strip()) > 10]
        for s in sentences:
            s_words = set(re.findall(r"\w+", s.lower()))
            overlap = len(q_words.intersection(s_words))
            candidate_sentences.append((overlap, s))

    candidate_sentences.sort(key=lambda x: x[0], reverse=True)
    if candidate_sentences and candidate_sentences[0][0] > 0:
        return f"{candidate_sentences[0][1]}."

    first_text = top_matches[0]["chunk"]["text"]
    return first_text[:250].strip() + ("..." if len(first_text) > 250 else "")

def search_top_chunks(query_vector: List[float], top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Scans every chunk stored in memory, calculates its cosine similarity
    against the question vector, and returns the top_k best matches.
    """
    all_chunks = store.get_all_chunks()
    if not all_chunks:
        return []

    scored_chunks = []
    for chunk in all_chunks:
        score = cosine_similarity(query_vector, chunk["embedding"])
        scored_chunks.append({
            "chunk": chunk,
            "score": score
        })

    # Sort descending: highest score first
    scored_chunks.sort(key=lambda x: x["score"], reverse=True)
    return scored_chunks[:top_k]


def generate_rag_answer(question: str, top_k: int = 3) -> Dict[str, Any]:
    """
    The full RAG execution:
    1. Embeds question -> 768-dim vector
    2. Retrieves top_k chunks using cosine similarity
    3. Builds prompt with numbered sources [1], [2]
    4. Calls Google Gemini Flash to synthesize response
    5. Returns answer + cited source metadata
    """
    logger.info("Executing RAG retrieval for question: '%s'", question)
    query_vector = get_embedding(question)

    top_matches = search_top_chunks(query_vector, top_k=top_k)

    if not top_matches:
        logger.info("No saved content available for RAG search")
        return {
            "question": question,
            "answer": "No items have been saved in your inbox yet. Please add some notes or URLs first!",
            "sources": []
        }

    # Format context and sources
    context_blocks = []
    sources = []

    for idx, match in enumerate(top_matches, start=1):
        chunk = match["chunk"]
        score = match["score"]
        title = chunk.get("title") or "Untitled"
        url = chunk.get("source_url")
        text = chunk["text"]

        context_blocks.append(f"[{idx}] (Source: {title}):\n{text}")
        sources.append({
            "source_id": idx,
            "item_id": chunk["item_id"],
            "title": title,
            "source_url": url,
            "snippet": text[:150] + ("..." if len(text) > 150 else ""),
            "similarity_score": round(score, 4)
        })

    formatted_context = "\n\n".join(context_blocks)

    system_instruction = (
        "You are a helpful knowledge assistant. "
        "Answer the user's question directly and naturally based strictly on the provided context snippets. "
        "Do not include bracket citation tags like [1] or [2] inside your answer text. "
        "If the answer cannot be found in the context, truthfully say: 'I couldn't find the answer in your saved inbox.'"
    )

    prompt = f"""{system_instruction}

Context Snippets:
{formatted_context}

User Question:
{question}

Answer:"""

    answer_text = ""
    client = get_gemini_client()
    
    if client is not None:
        # gemini-3.5-flash-lite delivers ~1s latency; fallbacks provided for resilience
        candidate_models = ["gemini-3.5-flash-lite", "gemini-3.5-flash", "gemini-3.8-flash"]
        for model_name in candidate_models:
            try:
                logger.info("Calling Gemini model '%s'...", model_name)
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                )
                raw_answer = response.text if response.text else ""
                if raw_answer:
                    # Automatically remove any bracket citation references like [1], [2] from the answer
                    cleaned = re.sub(r'\s*\[\d+\](?:\s*,\s*\[\d+\])*', '', raw_answer)
                    cleaned = re.sub(r'\s+\.', '.', cleaned)
                    cleaned = re.sub(r'\s+,', ',', cleaned)
                    answer_text = re.sub(r'  +', ' ', cleaned).strip()
                    logger.info("Gemini model '%s' responded successfully", model_name)
                    break
            except Exception as e:
                logger.warning("Gemini model '%s' encountered issue (%s). Trying fallback...", model_name, e)

    # If cloud LLM is unauthenticated (e.g. invalid/expired key) or offline, use intelligent extractive fallback
    if not answer_text:
        logger.info("Synthesizing answer via intelligent extractive RAG fallback.")
        answer_text = _extract_extractive_answer(question, top_matches)

    logger.info("RAG synthesis complete for question: '%s'", question)

    return {
        "question": question,
        "answer": answer_text,
        "sources": sources
    }
