"""
Database table definitions.

Each class below = one table. SQLAlchemy's declarative_base() lets us define
tables as normal Python classes instead of writing raw SQL CREATE TABLE
statements. This is the "ORM" (Object-Relational Mapping) part of the stack.
"""

from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from app.database.database import Base


class Mission(Base):
    """
    One row = one inspection mission requested by a user.

    Example: user says "inspect the north rooftop for cracks" ->
    this row stores that raw request plus the structured params
    extracted from it (location, target, altitude, etc).
    """
    __tablename__ = "missions"

    id = Column(Integer, primary_key=True, index=True)
    raw_request = Column(Text, nullable=False)            # original NL request
    mission_type = Column(String, default="inspection")
    location = Column(String, nullable=True)              # e.g. "north rooftop"
    inspection_target = Column(String, nullable=True)     # e.g. "cracks"
    altitude_m = Column(Float, nullable=True)             # planned flight altitude
    waypoints = Column(JSON, nullable=True)               # list of [lat, lon, alt]
    status = Column(String, default="pending")            # pending/in_progress/complete/failed
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # one mission -> many anomalies found during that mission
    anomalies = relationship("Anomaly", back_populates="mission", cascade="all, delete-orphan")
    # one mission -> one report
    report = relationship("InspectionReport", back_populates="mission", cascade="all, delete-orphan", uselist = False)


class Anomaly(Base):
    """
    One row = one defect/anomaly detected by the CV model during a mission.
    Foreign key ties it back to the mission it was found in.
    """
    __tablename__ = "anomalies"

    id = Column(Integer, primary_key=True, index=True)
    mission_id = Column(Integer, ForeignKey("missions.id"), nullable=False)

    image_path = Column(String, nullable=False)          # which captured image this came from
    label = Column(String, nullable=False)               # e.g. "crack", "rust", "corrosion"
    confidence = Column(Float, nullable=False)            # model confidence 0-1
    bbox = Column(JSON, nullable=True)                    # [x1, y1, x2, y2] bounding box
    detected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    mission = relationship("Mission", back_populates="anomalies")


class InspectionReport(Base):
    """
    One row = one generated report summarizing a mission's findings.
    This is the human-readable output the agent produces at the end.
    """
    __tablename__ = "inspection_reports"

    id = Column(Integer, primary_key=True, index=True)
    mission_id = Column(Integer, ForeignKey("missions.id"), nullable=False, unique=True)

    summary = Column(Text, nullable=False)                # LLM-generated summary text
    recommendations = Column(Text, nullable=True)
    anomaly_count = Column(Integer, default=0)
    file_path = Column(String, nullable=True)             # where the .md/.pdf report was saved
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    mission = relationship("Mission", back_populates="report")