"""
Pydantic schemas = the "shape" of data for API requests/responses.

Different from database/models.py:
- models.py defines what's stored in the DB (SQLAlchemy)
- schemas.py defines what the API accepts/returns (Pydantic)

FastAPI uses these to auto-validate incoming requests and auto-generate
API docs (visit /docs once the server's running to see this in action).
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


# Requests 

class MissionRequest(BaseModel):
    """What the user sends to kick off a new mission."""
    raw_request: str  # e.g. "inspect the north rooftop for cracks"


# Responses 

class AnomalyResponse(BaseModel):
    id: int
    image_path: str
    label: str
    confidence: float
    bbox: Optional[List[float]] = None
    detected_at: datetime

    class Config:
        from_attributes = True  # lets Pydantic read directly from SQLAlchemy objects


class ReportResponse(BaseModel):
    id: int
    summary: str
    recommendations: Optional[str] = None
    anomaly_count: int
    file_path: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class MissionResponse(BaseModel):
    id: int
    raw_request: str
    mission_type: str
    location: Optional[str] = None
    inspection_target: Optional[str] = None
    altitude_m: Optional[float] = None
    waypoints: Optional[List[List[float]]] = None
    status: str
    created_at: datetime
    anomalies: List[AnomalyResponse] = []
    report: Optional[ReportResponse] = None

    class Config:
        from_attributes = True