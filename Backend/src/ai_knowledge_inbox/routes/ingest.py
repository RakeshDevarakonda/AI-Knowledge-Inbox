import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException

from ai_knowledge_inbox.schemas import IngestRequest, IngestResponse
from ai_knowledge_inbox.storage import store
from ai_knowledge_inbox.services.chunker import chunk_text
from ai_knowledge_inbox.services.embedding import get_embedding
from ai_knowledge_inbox.services.scraper import scrape_url
from ai_knowledge_inbox.config import logger

router = APIRouter(tags=["Ingestion"])

@router.post("/ingest", response_model=IngestResponse, status_code=201)
async def ingest_item(payload: IngestRequest):
    """
    Ingest a plain text note OR scrape content from a web URL,
    then automatically chunk it, generate embeddings, and store it.
    """
    item_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    logger.info("Ingest request received for source_type: '%s'", payload.source_type)

    # 1. Handle "note"
    if payload.source_type == "note":
        if not payload.content or not payload.content.strip():
            logger.warning("Ingest validation failed: note content is empty")
            raise HTTPException(status_code=400, detail="Content cannot be empty for a note.")
        
        text = payload.content.strip()
        title = payload.title or (text.split("\n")[0][:30] + ("..." if len(text) > 30 else ""))
        source_url = None

    # 2. Handle "url"
    elif payload.source_type == "url":
        if not payload.url or not payload.url.strip():
            logger.warning("Ingest validation failed: URL is empty")
            raise HTTPException(status_code=400, detail="URL cannot be empty for source_type 'url'.")
        
        logger.info("Scraping webpage URL: %s", payload.url.strip())
        scraped = await scrape_url(payload.url.strip())
        text = scraped["text"]
        title = payload.title or scraped["title"]
        source_url = payload.url.strip()

    else:
        raise HTTPException(status_code=400, detail="source_type must be either 'note' or 'url'.")

    # 3. Save parent document in memory
    item = {
        "id": item_id,
        "source_type": payload.source_type,
        "title": title,
        "content": text,
        "source_url": source_url,
        "created_at": now,
    }
    store.add_item(item)

    # 4. Chunk the text
    text_chunks = chunk_text(text)
    logger.info("Split item '%s' into %d chunks", title, len(text_chunks))

    # 5. Embed and save chunks
    saved_chunks = []
    try:
        for idx, chunk_str in enumerate(text_chunks):
            embedding_vector = get_embedding(chunk_str)
            chunk_obj = {
                "id": f"{item_id}_{idx}",
                "item_id": item_id,
                "title": title,
                "source_url": source_url,
                "chunk_index": idx,
                "text": chunk_str,
                "embedding": embedding_vector,
            }
            saved_chunks.append(chunk_obj)
    except Exception as e:
        logger.error("Embedding generation failed for item %s: %s", item_id, str(e))
        raise HTTPException(status_code=500, detail=f"Embedding generation failed: {str(e)}")

    store.add_chunks(saved_chunks)
    logger.info("Successfully indexed item '%s' with %d chunks", title, len(saved_chunks))

    return {
        "message": f"{payload.source_type.capitalize()} ingested and embedded successfully",
        "item": item,
        "chunks_created": len(saved_chunks)
    }
