from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class ReconcileRequest(BaseModel):
    amount: float = Field(..., description="Amount to match")
    date: str = Field(..., description="Date in ISO format (YYYY-MM-DD)")
    contact: Optional[str] = Field(None, description="Contact name to match")
    
    top_n: int = Field(3, description="Number of top matches to return", ge=1, le=50)
    threshold: float = Field(0.8, description="Minimum similarity score (0-1)", ge=0, le=1)
    factors: List[str] = Field(
        ["amount", "date", "contact"],
        description="Factors to consider: amount, date, contact"
    )
    weights: Optional[Dict[str, float]] = Field(
        None,
        description="Custom weights for factors (default: amount=0.90, date=0.05, contact=0.05)"
    )
    date_method: str = Field(
        "exponential",
        description="Date scoring method: 'linear' or 'exponential'"
    )


class MatchResult(BaseModel):
    score: float = Field(..., description="Similarity score (0-1)")
    input: Dict[str, Any] = Field(..., description="Input data submitted")
    invoice: Dict[str, Any] = Field(..., description="Matched invoice from database")


class ReconcileResponse(BaseModel):
    matches: List[MatchResult]
    total_matches: int = Field(..., description="Number of matches above threshold")
    total_invoices: int = Field(..., description="Total invoices in database")
    request_params: Dict[str, Any] = Field(..., description="Parameters used for matching")
