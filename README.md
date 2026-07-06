<div align="center">

# Autonomous Drone Mission Planner Agent

</div>

---

## Overview

An agentic AI pipeline that converts natural language drone inspection requests into structured mission execution. A LangChain tool-calling agent orchestrates extraction, flight planning, simulated flight, object detection, and automated report generation, with results persisted to PostgreSQL and surfaced through a Streamlit dashboard.

---

## Pipeline

<table>
  <tr><th>Stage</th><th>Component</th><th>Description</th></tr>
  <tr><td>1. Extraction</td><td><code>mission/extractor.py</code></td><td>LLM (Groq, via LangChain) parses raw text into structured fields — location, inspection target, altitude</td></tr>
  <tr><td>2. Planning</td><td><code>mission/planner.py</code></td><td>Deterministic geometry — generates a circular waypoint path</td></tr>
  <tr><td>3. Simulation</td><td><code>mission/simulator.py</code></td><td>Simulates flying the route and capturing images at each waypoint</td></tr>
  <tr><td>4. Detection</td><td><code>vision/detector.py</code></td><td>YOLO11 (Ultralytics) runs object detection on each captured image</td></tr>
  <tr><td>5. Reporting</td><td><code>reports/generator.py</code></td><td>LLM synthesizes detections into a written summary and recommendations</td></tr>
</table>

All five stages are wrapped as LangChain tools and orchestrated by a tool-calling agent that reasons about the correct sequence based on real intermediate outputs.

---

## Architecture

<pre>
app/
├── agent/       # LangChain tool-calling agent (tools, prompt, executor)
├── backend/     # FastAPI app, routes, Pydantic schemas
├── database/    # SQLAlchemy models, connection setup, CRUD operations
├── mission/     # Extraction, waypoint planning, flight simulation
├── vision/      # YOLO-based object detection
├── reports/     # LLM-based report generation
└── frontend/    # Streamlit dashboard
</pre>

The database layer uses SQLAlchemy, so the same application code runs against either SQLite (local development) or PostgreSQL (production) — only the connection string changes.

---

## Data Model

<table>
  <tr>
    <th>Table</th>
    <th>Purpose</th>
  </tr>
  <tr>
    <td><code>missions</code></td>
    <td>One row per inspection request — raw text, extracted parameters, waypoints, status</td>
  </tr>
  <tr>
    <td><code>anomalies</code></td>
    <td>One row per object detected during a mission — label, confidence, bounding box</td>
  </tr>
  <tr>
    <td><code>inspection_report</code></td>
    <td>One row per mission — generated summary and recommendations</td>
  </tr>
</table>

<br>

---

## Technologies Used

<ul>
  <li>Python</li>
  <li>LangChain, LangGraph (<code>create_agent</code>)</li>
  <li>Groq (LLM inference)</li>
  <li>YOLO11 / Ultralytics</li>
  <li>FastAPI</li>
  <li>SQLAlchemy, PostgreSQL</li>
  <li>Streamlit</li>
</ul>

---

## Setup

<ol>
  <li>
    Clone the repository, create a virtual environment, and install dependencies:
    <pre><code>python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt</code></pre>
  </li>

  <li>
    Create a <code>.env</code> file:
    <pre><code>GROQ_API_KEY=your_groq_api_key
DATABASE_URL=postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/drone_agent</code></pre>

    SQLite also works with no code changes:
    <pre><code>DATABASE_URL=sqlite:///./drone_agent.db</code></pre>
  </li>

  <li>
    Create the PostgreSQL database:
    <pre><code>CREATE DATABASE drone_agent;</code></pre>
  </li>

  <li>
    Run the backend:
    <pre><code>uvicorn app.backend.main:app --reload</code></pre>

    API docs will be available at:
    <code>http://127.0.0.1:8000/docs</code>
  </li>

  <li>
    Run the dashboard (in a separate terminal):
    <pre><code>streamlit run app/frontend/streamlit_app.py</code></pre>
  </li>
</ol>

---

## Known Limitations

<ul>
  <li><b>Detection is general-purpose, not defect-specific</b> — YOLO11 uses pretrained COCO weights (people, vehicles, everyday objects), not a model fine-tuned on structural defects such as cracks or corrosion. Real defect detection would require fine-tuning on a labeled dataset.</li>

  <li><b>Flight is simulated</b> — there is no physical drone; captured images are sampled from a small local test folder standing in for a live camera feed.</li>

  <li><b>Detection is target-agnostic</b> — the detector reports every object it recognizes regardless of the mission's stated inspection target. Relevance is only reasoned about narratively during report generation and is not enforced during detection.</li>

</ul>

---

## Conclusion

This project demonstrates a complete agentic pipeline that combines natural language understanding, deterministic flight planning, computer vision-based analysis, automated report generation, relational data persistence, and REST API/dashboard interfaces.

The project serves as an example of how LLM agents can orchestrate multiple specialized components to transform a simple natural language instruction into an end-to-end autonomous workflow.

---

## Author

<b>Mohammed Maaz Ali</b><br>
B.Tech in Computer Science and Engineering, IIIT Kottayam
