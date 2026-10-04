"""
Pydantic schemas for health and system status endpoints.
"""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response schema."""
    status: str = Field(..., description="Service status, e.g. 'ok'")
    project: str = Field(..., description="Project name")
    version: str = Field(..., description="Project edition / version")
