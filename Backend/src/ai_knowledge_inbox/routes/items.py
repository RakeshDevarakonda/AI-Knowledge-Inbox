from fastapi import APIRouter
from ai_knowledge_inbox.storage import store
from ai_knowledge_inbox.schemas import ItemsListResponse
from ai_knowledge_inbox.config import logger

router = APIRouter(tags=["Items"])

@router.get("/items", response_model=ItemsListResponse)
def get_items():
    """
    Retrieve all saved notes and URLs from the inbox, sorted newest first.
    """
    items = store.get_all_items()
    logger.info("Retrieved %d items from inbox", len(items))
    return {
        "items": items,
        "total": len(items)
    }
