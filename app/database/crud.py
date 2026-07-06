"""
CRUD = Create, Read, Update, Delete.

This file is the *only* place in the app that should directly query the
database. Routes, the agent's tools, everything else calls these functions
instead of writing raw SQLAlchemy queries inline. Keeps DB logic in one spot.
"""

from sqlalchemy.orm import Session
from app.database import models


# Mission

def create_mission(db: Session, raw_request: str) -> models.Mission:
    """Create a new mission row from the raw natural-language request."""
    mission = models.Mission(raw_request=raw_request, status="pending")
    db.add(mission)
    db.commit()
    db.refresh(mission)  # pulls back the auto-generated id, created_at, etc.
    return mission


def update_mission_params(
    db: Session,
    mission_id: int,
    mission_type: str = None,
    location: str = None,
    inspection_target: str = None,
    altitude_m: float = None,
) -> models.Mission:
    """Update a mission with extracted params (from the extractor tool)."""
    mission = db.query(models.Mission).filter(models.Mission.id == mission_id).first()
    if not mission:
        return None
    if location is not None:
        mission.location = location
    if inspection_target is not None:
        mission.inspection_target = inspection_target
    if altitude_m is not None:
        mission.altitude_m = altitude_m
    if mission_type is not None:
        mission.mission_type = mission_type
    db.commit()
    db.refresh(mission)
    return mission


def update_mission_waypoints(db: Session, mission_id: int, waypoints: list) -> models.Mission:
    """Attach a planned flight path to a mission."""
    mission = db.query(models.Mission).filter(models.Mission.id == mission_id).first()
    if not mission:
        return None
    mission.waypoints = waypoints
    db.commit()
    db.refresh(mission)
    return mission


def update_mission_status(db: Session, mission_id: int, status: str) -> models.Mission:
    """Move a mission through its lifecycle: pending -> in_progress -> complete/failed."""
    mission = db.query(models.Mission).filter(models.Mission.id == mission_id).first()
    if not mission:
        return None
    mission.status = status
    db.commit()
    db.refresh(mission)
    return mission


def get_mission(db: Session, mission_id: int) -> models.Mission:
    return db.query(models.Mission).filter(models.Mission.id == mission_id).first()


def get_all_missions(db: Session):
    return db.query(models.Mission).order_by(models.Mission.created_at.desc()).all()


#   Anomaly        

def create_anomaly(
    db: Session,
    mission_id: int,
    image_path: str,
    label: str,
    confidence: float,
    bbox: list = None,
) -> models.Anomaly:
    """Log one detected defect against a mission."""
    anomaly = models.Anomaly(
        mission_id=mission_id,
        image_path=image_path,
        label=label,
        confidence=confidence,
        bbox=bbox,
    )
    db.add(anomaly)
    db.commit()
    db.refresh(anomaly)
    return anomaly


def get_anomalies_for_mission(db: Session, mission_id: int):
    return db.query(models.Anomaly).filter(models.Anomaly.mission_id == mission_id).all()


# InspectionReport 

def create_report(
    db: Session,
    mission_id: int,
    summary: str,
    anomaly_count: int,
    recommendations: str = None,
    file_path: str = None,
) -> models.InspectionReport:
    """Save the final generated report for a mission."""
    report = models.InspectionReport(
        mission_id=mission_id,
        summary=summary,
        anomaly_count=anomaly_count,
        recommendations=recommendations,
        file_path=file_path,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def get_report_for_mission(db: Session, mission_id: int) -> models.InspectionReport:
    return (
        db.query(models.InspectionReport)
        .filter(models.InspectionReport.mission_id == mission_id)
        .first()
    )