"""
Agent executor: wires the system prompt, tools, and LLM together into a
runnable agent that reasons about which tool to call, in what order,
based on the mission request.

Uses LangChain 1.x's create_agent (built on LangGraph under the hood) --
the current replacement for the older create_tool_calling_agent + AgentExecutor pattern.
"""

import os
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from dotenv import load_dotenv

from app.agent.prompts import SYSTEM_PROMPT
from app.agent.tools import ALL_TOOLS

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0,  # deterministic tool-calling decisions, not creative
)

agent = create_agent(
    model=llm,
    tools=ALL_TOOLS,
    system_prompt=SYSTEM_PROMPT,
    debug=True,   # prints each node/tool execution step -- this is the modern equivalent of the old verbose=True
)


def run_mission(raw_request: str) -> dict:
    """
    Entry point: runs the full agentic pipeline for one mission request.
    debug=True on the agent prints each tool call/step as it happens.
    """
    result = agent.invoke({
        "messages": [{"role": "user", "content": raw_request}]
    })

    final_message = result["messages"][-1]
    return {"output": final_message.content}