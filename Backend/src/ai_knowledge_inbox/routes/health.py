from fastapi import APIRouter

router = APIRouter(tags=["Health"])

@router.get("/")
def root():
    return {
        "service": "AI Knowledge Inbox API",
        "status": "online",
        "docs_url": "/docs"
    }

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "AI Knowledge Inbox"
    }
