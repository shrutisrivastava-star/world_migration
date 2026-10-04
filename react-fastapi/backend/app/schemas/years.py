"""
Pydantic schemas for census observation years endpoint.
"""

from typing import List
from pydantic import BaseModel, Field


class YearsResponse(BaseModel):
    """Observation years response schema."""
    years: List[int] = Field(..., description="List of valid UN DESA census observation years")
