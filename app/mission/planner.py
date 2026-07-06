"""
Mission planner: turns structured mission params into a waypoint path.

Deliberately NOT LLM-based -- waypoint generation is a deterministic
geometry problem, not a language understanding problem.
"""

import math

CENTER_LAT = 28.6139   # placeholder GPS coords -- in a real system these
CENTER_LON = 77.2090   # would come from the site being inspected


def plan_mission(altitude_m: float = 30.0, radius_m: float = 20.0, num_points: int = 6) -> list:
    """
    Generates a simple circular flight path around a center point --
    a drone orbiting a structure at a fixed altitude to inspect it
    from all sides. Returns a list of [lat, lon, altitude] waypoints.
    """
    waypoints = []
    for i in range(num_points):
        angle = (2 * math.pi / num_points) * i
        # rough meters-to-degrees conversion -- good enough for a demo,
        # not accurate for real navigation (real systems use geodesic math)
        d_lat = (radius_m * math.cos(angle)) / 111320
        d_lon = (radius_m * math.sin(angle)) / (111320 * math.cos(math.radians(CENTER_LAT)))
        waypoints.append([
            round(CENTER_LAT + d_lat, 6),
            round(CENTER_LON + d_lon, 6),
            altitude_m,
        ])
    waypoints.append(waypoints[0])  # close the loop
    return waypoints