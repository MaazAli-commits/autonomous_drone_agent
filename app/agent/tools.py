"""
LangChain tools: thin wrappers around existing mission/vision functions
so the agent can call them. Each tool does ONE job and calls into code
we already built and tested (extractor, planner, simulator, detector,
report generator) -- no new logic lives here.
"""

from langchain_core.tools import tool
from app.mission.extractor import extract_mission_params
from app.mission.planner import plan_mission
from app.mission.simulator import simulate_flight
from app.vision.detector import detect_anomalies
from app.reports.generator import generate_report


@tool
def extract_params_tool(raw_request: str) -> dict:
    """Extract structured mission parameters (location, target, altitude) from a raw natural language request."""
    return extract_mission_params(raw_request)


@tool
def plan_route_tool(altitude_m: float) -> list:
    """Generate a list of [lat, lon, altitude] waypoints for the drone to fly, given a flight altitude."""
    return plan_mission(altitude_m=altitude_m)


@tool
def fly_and_capture_tool(waypoints: list) -> list:
    """Simulate flying the drone along the given waypoints and capturing an image at each one. Returns a list of {waypoint, image_path} dicts."""
    return simulate_flight(waypoints)


@tool
def detect_objects_tool(image_path: str) -> list:
    """Run YOLOv8 object detection on a single captured image. Returns a list of {label, confidence, bbox} detections."""
    return detect_anomalies(image_path)


@tool
def write_report_tool(raw_request: str, location: str, detections: list) -> dict:
    """Write a human-readable inspection summary and recommendations given the original request, location, and all detections found."""
    return generate_report(raw_request, location, detections)


ALL_TOOLS = [
    extract_params_tool,
    plan_route_tool,
    fly_and_capture_tool,
    detect_objects_tool,
    write_report_tool,
]