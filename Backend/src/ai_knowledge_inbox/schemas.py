from pydantic import BaseModel, Field
from typing import Optional, List, Literal

# ----------------- Ingestion Schemas -----------------
class IngestRequest(BaseModel):
    source_type: Literal["note", "url"] = Field(..., description="Type of source: 'note' or 'url'")
    content: Optional[str] = Field(None, description="Plain text (required if source_type is 'note')")
    url: Optional[str] = Field(None, description="Web URL to scrape (required if source_type is 'url')")
    title: Optional[str] = Field(None, description="Optional custom title")

class ItemResponse(BaseModel):
    id: str
    source_type: str
    title: str
    content: str
    source_url: Optional[str] = None
    created_at: str

class IngestResponse(BaseModel):
    message: str
    item: ItemResponse
    chunks_created: int

# ----------------- Items List Schemas -----------------
class ItemsListResponse(BaseModel):
    items: List[ItemResponse]
    total: int

# ----------------- Query (RAG) Schemas -----------------
class QueryRequest(BaseModel):
    question: str = Field(..., min_length=2, description="Question to ask over saved content")
    top_k: Optional[int] = Field(3, ge=1, le=10, description="Number of top chunks to retrieve")

class CitedSource(BaseModel):
    source_id: int
    item_id: str
    title: str
    source_url: Optional[str] = None
    snippet: str
    similarity_score: float

class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: List[CitedSource]

# ----------------- Error Schemas -----------------
class ErrorDetail(BaseModel):
    status_code: int
    message: str
    error_type: str
    path: Optional[str] = None

class ErrorResponse(BaseModel):
    success: bool = False
    detail: str
    message: str
    error: ErrorDetail
