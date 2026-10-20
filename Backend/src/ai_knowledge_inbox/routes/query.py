from fastapi import APIRouter, HTTPException

from ai_knowledge_inbox.schemas import QueryRequest, QueryResponse
from ai_knowledge_inbox.services.rag import generate_rag_answer
from ai_knowledge_inbox.config import logger

router = APIRouter(tags=["Query & RAG"])

@router.post("/query", response_model=QueryResponse)
def query_knowledge(payload: QueryRequest):
    """
    Ask a question across all saved notes and URLs.
    Retrieves relevant chunks via vector similarity and generates an answer with cited sources.
    """
    logger.info("RAG query received: '%s' (top_k=%d)", payload.question, payload.top_k or 3)
    try:
        result = generate_rag_answer(
            question=payload.question,
            top_k=payload.top_k or 3,
        )
        logger.info("RAG query successful. Returned %d source citations", len(result.get("sources", [])))
        return result
    except ValueError as ve:
        logger.warning("RAG user error: %s", ve)
        raise HTTPException(status_code=400, detail=str(ve))
    except TimeoutError as te:
        logger.error("RAG timeout: %s", te)
        raise HTTPException(status_code=504, detail=str(te))
    except Exception as e:
        logger.error("RAG query failed for '%s': %s", payload.question, str(e))
        raise HTTPException(status_code=500, detail=f"RAG query failed: {str(e)}")
