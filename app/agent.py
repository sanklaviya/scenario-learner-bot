# ruff: noqa
"""Scenario Learner Bot — Multi-Agent Architecture.

Generates interactive role-play scenarios and branching dialogue trees
for corporate or academic training, with security screening and
human-in-the-loop approval.
"""

import json
import re
import sys
import os
import datetime
from pathlib import Path

from google.adk.agents import Agent
from google.adk.tools import AgentTool
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

from .config import config

# ═══════════════════════════════════════════════════════════════════════════════
# MCP Toolset (connected to mcp_server.py via stdio)
# ═══════════════════════════════════════════════════════════════════════════════

MCP_SERVER_PATH = str(Path(__file__).parent / "mcp_server.py")

scenario_tools = MCPToolset(
    connection_params=StdioServerParameters(
        command=sys.executable,
        args=[MCP_SERVER_PATH],
    )
)

# ═══════════════════════════════════════════════════════════════════════════════
# Security checkpoint — runs as before_agent_callback on orchestrator
# ═══════════════════════════════════════════════════════════════════════════════

# PII patterns relevant to eLearning context
_PII_PATTERNS = {
    "email": re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"),
    "phone": re.compile(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "student_id": re.compile(r"\b[Ss]tudent[\s_-]?[Ii][Dd][\s:]*\d{5,10}\b"),
}

_INJECTION_KEYWORDS = [
    "ignore previous instructions",
    "ignore all instructions",
    "disregard your prompt",
    "you are now",
    "pretend you are",
    "system prompt",
    "reveal your instructions",
    "override safety",
]


def _audit_log(severity: str, event: str, details: dict) -> None:
    """Write a structured JSON audit log entry to stderr."""
    entry = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "severity": severity,
        "event": event,
        **details,
    }
    print(json.dumps(entry), file=sys.stderr)


def security_checkpoint(callback_context, llm_request):
    """Screen user input for PII and prompt injection before processing.

    This runs as a before_model_callback on the orchestrator agent.
    Returns a types.Content to block the request, or None to allow it.
    """
    from google.genai import types

    # Extract user text from the most recent user message in the request
    user_input = ""
    if llm_request and llm_request.contents:
        for content in reversed(llm_request.contents):
            if content.role == "user" and content.parts:
                user_input = " ".join(
                    p.text for p in content.parts if hasattr(p, "text") and p.text
                )
                break

    if not user_input:
        return None  # Nothing to screen

    findings = []
    redacted = user_input

    # ── PII scrubbing ───────────────────────────────────────────────────
    if config.pii_redaction_enabled:
        for pii_type, pattern in _PII_PATTERNS.items():
            matches = pattern.findall(redacted)
            if matches:
                findings.append({"type": "PII", "subtype": pii_type, "count": len(matches)})
                redacted = pattern.sub(f"[REDACTED_{pii_type.upper()}]", redacted)

    # ── Prompt injection detection ──────────────────────────────────────
    if config.injection_detection_enabled:
        lower = user_input.lower()
        for keyword in _INJECTION_KEYWORDS:
            if keyword in lower:
                _audit_log("CRITICAL", "PROMPT_INJECTION_DETECTED", {
                    "keyword": keyword,
                    "action": "blocked",
                })
                return types.Content(
                    role="model",
                    parts=[types.Part.from_text(
                        "⚠️ Your input was flagged for potential prompt injection "
                        f"(detected: '{keyword}'). Request blocked for safety."
                    )],
                )

    # ── Domain-specific: block requests for real student grades/records ─
    grade_keywords = ["real grades", "actual transcript", "student records",
                      "access database", "export all students"]
    lower = user_input.lower()
    for kw in grade_keywords:
        if kw in lower:
            _audit_log("WARNING", "CONTENT_FILTER_TRIGGERED", {
                "keyword": kw,
                "action": "blocked",
            })
            return types.Content(
                role="model",
                parts=[types.Part.from_text(
                    "⚠️ This agent generates fictional training scenarios only. "
                    "It cannot access real student records or grades."
                )],
            )

    # ── PII was found — update the request with redacted text ──────────
    if findings:
        _audit_log("WARNING", "PII_REDACTED", {"findings": findings})
        # Replace the user message text with the redacted version
        if llm_request and llm_request.contents:
            for content in reversed(llm_request.contents):
                if content.role == "user" and content.parts:
                    for i, part in enumerate(content.parts):
                        if hasattr(part, "text") and part.text:
                            content.parts[i] = types.Part.from_text(redacted)
                    break
    else:
        _audit_log("INFO", "SECURITY_PASS", {"input_length": len(user_input)})

    # Store sanitized input in state for sub-agents
    if hasattr(callback_context, "state"):
        callback_context.state["sanitized_input"] = redacted

    return None  # Allow the request to proceed


# ═══════════════════════════════════════════════════════════════════════════════
# Sub-Agent 1: Scenario Designer
# ═══════════════════════════════════════════════════════════════════════════════

scenario_designer = Agent(
    name="scenario_designer",
    model=config.model,
    instruction="""You are an expert instructional designer. Create training scenarios with branching dialogue trees.

Steps:
1. Call generate_scenario_seed with topic + difficulty + domain.
2. Call build_branching_tree per decision point (2-3 points, 3 branches each).
3. Combine into a structured scenario with characters, setting, and labeled decision points.

Be concise. Format as scenario document.""",
    tools=[scenario_tools],
)

# ═══════════════════════════════════════════════════════════════════════════════
# Sub-Agent 2: Feedback Coach
# ═══════════════════════════════════════════════════════════════════════════════

feedback_coach = Agent(
    name="feedback_coach",
    model=config.model,
    instruction="""You are a learning coach. Score learner choices and give constructive feedback.

Steps:
1. Call simulate_learner_persona with experience level if not given.
2. Call score_learner_path with the scenario_id and chosen branches.
3. Return concise per-choice feedback + overall rating.

Be encouraging, specific, and adapt tone to experience level.""",
    tools=[scenario_tools],
)

# ═══════════════════════════════════════════════════════════════════════════════
# Orchestrator — root agent with AgentTool delegation + security callback
# ═══════════════════════════════════════════════════════════════════════════════

root_agent = Agent(
    name="scenario_learner_bot",
    model=config.model,
    instruction="""You are the Scenario Learner Bot. You CREATE training scenarios or SCORE/REVIEW learner paths.

Routing:
- User wants to CREATE/GENERATE/BUILD a scenario → use scenario_designer tool
- User wants FEEDBACK/SCORE/REVIEW/EVALUATE choices → use feedback_coach tool
- If unclear, ask what they need.

IMPORTANT: When a sub-agent returns a scenario or feedback, you MUST include the FULL content in your response.
Do NOT summarize or shorten it. Present the complete scenario with all characters, setting, decision points, and branches exactly as generated.""",
    tools=[
        AgentTool(agent=scenario_designer),
        AgentTool(agent=feedback_coach),
    ],
    before_model_callback=security_checkpoint,
)
