"""
API route definitions.

The create endpoint calls the mission pipeline functions directly, in
sequence, rather than going through the LangChain agent -- the agent
(app/agent/agent_executor.py) is a separately tested component; here
the order is fixed and known, so plain function calls are simpler and
more reliable than parsing an LLM's tool-call history.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database import crud
from app.backend.schemas import MissionRequest, MissionResponse
from app.mission.extractor import extract_mission_params
from app.mission.planner import plan_mission
from app.mission.simulator import simulate_flight
from app.vision.detector import detect_anomalies
from app.reports.generator import generate_report

router = APIRouter(prefix="/missions", tags=["missions"])


@router.post("/", response_model=MissionResponse)
def create_mission(request: MissionRequest, db: Session = Depends(get_db)):
    """Runs the full mission pipeline and saves the results."""
    mission = crud.create_mission(db, raw_request=request.raw_request)
    crud.update_mission_status(db, mission.id, "in_progress")

    try:
        params = extract_mission_params(request.raw_request)
        crud.update_mission_params(
            db, mission.id,
            location=params.get("location"),
            inspection_target=params.get("inspection_target"),
            altitude_m=params.get("altitude_m"),
            mission_type=params.get("mission_type"),
        )

        waypoints = plan_mission(altitude_m=params.get("altitude_m") or 30.0)
        crud.update_mission_waypoints(db, mission.id, waypoints)

        captures = simulate_flight(waypoints)

        all_detections = []
        for capture in captures:
            detections = detect_anomalies(capture["image_path"])
            for d in detections:
                crud.create_anomaly(
                    db, mission_id=mission.id,
                    image_path=capture["image_path"],
                    label=d["label"], confidence=d["confidence"], bbox=d.get("bbox"),
                )
            all_detections.extend(detections)

        report = generate_report(request.raw_request, params.get("location"), all_detections)
        crud.create_report(
            db, mission_id=mission.id,
            summary=report["summary"],
            recommendations=report["recommendations"],
            anomaly_count=len(all_detections),
        )

        crud.update_mission_status(db, mission.id, "complete")

    except Exception as e:
        crud.update_mission_status(db, mission.id, "failed")
        raise HTTPException(status_code=500, detail=f"Mission pipeline failed: {str(e)}")

    db.refresh(mission)
    return mission


@router.get("/", response_model=list[MissionResponse])
def list_missions(db: Session = Depends(get_db)):
    return crud.get_all_missions(db)


@router.get("/{mission_id}", response_model=MissionResponse)
def get_mission(mission_id: int, db: Session = Depends(get_db)):
    mission = crud.get_mission(db, mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    return mission