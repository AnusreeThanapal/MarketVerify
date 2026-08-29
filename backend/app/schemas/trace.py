from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from pydantic import Field
from backend.app.schemas.common import BaseSchema


class TraceEntry(BaseSchema):
    agent: str = Field(..., description="Name of the agent executing the step")
    step_index: int = Field(0, description="Chronological index of this trace step")
    input_summary: str = Field(..., description="Summary of input passed to the agent")
    retrieved_doc_ids: List[str] = Field(default_factory=list, description="IDs of documents retrieved from vector stores")
    retrieved_docs_preview: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list, description="Lightweight snippet of retrieved evidence"
    )
    output_summary: str = Field(..., description="Summary of agent output decisions")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional agent-specific diagnostics")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="Timestamp of execution"
    )
