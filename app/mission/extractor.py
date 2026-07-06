"""
Mission extractor: turns a raw natural-language request into structured
mission parameters using an LLM (Groq), via LangChain's structured output
binding -- guarantees valid, schema-matching output instead of parsing
raw JSON text from a prompt.
"""

import os
from pydantic import BaseModel, Field
from typing import Optional
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0,
)


class MissionParams(BaseModel):
    location: Optional[str] = Field(
        description="The PLACE being inspected -- a physical area/site, e.g. 'the parking area', 'north rooftop', 'the west wing'. This is WHERE the drone flies to, not what it's looking for. Null only if no place is mentioned at all."
    )
    inspection_target: Optional[str] = Field(
        description="What the drone is looking FOR at that location -- the defect, object, or condition of interest, e.g. 'unauthorized vehicles', 'cracks', 'rust'. This is NOT the place itself. Null if not mentioned."
    )
    altitude_m: float = Field(description="Flight altitude in meters. Default to 30 if not specified.")
    mission_type: str = Field(description="One of: inspection, mapping, delivery. Default to 'inspection'.")


prompt = ChatPromptTemplate.from_template(
    """You are a mission parameter extractor for a drone inspection system.

Extract these fields from the request:
- location: the PLACE being inspected (where the drone flies to), e.g. "the parking area", "north rooftop". NOT what it's looking for.
- inspection_target: what the drone is looking FOR at that location, e.g. "unauthorized vehicles", "cracks". NOT the place itself.
- altitude_m: flight altitude in meters, default 30 if not specified.
- mission_type: one of inspection, mapping, delivery. Default 'inspection'.

Example: "inspect the parking area for unauthorized vehicles"
-> location: "the parking area", inspection_target: "unauthorized vehicles"

Request: "{request}"
"""
)

structured_llm = llm.with_structured_output(MissionParams)
extraction_chain = prompt | structured_llm


def extract_mission_params(raw_request: str) -> dict:
    """
    Runs the chain to parse raw_request into structured params.
    Returns a plain dict for compatibility with the rest of the pipeline.
    """
    result: MissionParams = extraction_chain.invoke({"request": raw_request})
    return result.model_dump()