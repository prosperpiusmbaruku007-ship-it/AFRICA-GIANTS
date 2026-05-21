from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class ScrapedDocument(BaseModel):
    """Schema for raw scraped business/regulatory documents."""
    url: str
    source_name: str  # e.g., TRA, BRELA
    title: str
    raw_content: str
    scraped_at: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class CleanedDocument(BaseModel):
    """Schema for cleaned and normalized documents ready for CPT/chunking."""
    doc_id: str
    source_name: str
    url: str
    cleaned_content: str
    language: str  # e.g., sw (Swahili), en (English)
    cleaned_at: str

class QAPair(BaseModel):
    """Schema for instruction tuning training pairs."""
    instruction: str = Field(description="The question or prompt for the model")
    input: str = Field(default="", description="Optional context block")
    output: str = Field(description="The correct assistant response")
    source_doc_id: Optional[str] = None
    category: str = "general"  # e.g., tax, registration, banking

class EvaluationResult(BaseModel):
    """Schema for recording the metrics of a candidate model run."""
    model_name: str
    dataset_version: str
    timestamp: str
    loss: float
    perplexity: Optional[float] = None
    accuracy_score: float
    hallucination_rate: float
    p95_latency_ms: float
    passed_gate: bool
    metrics_breakdown: Dict[str, Any] = Field(default_factory=dict)
