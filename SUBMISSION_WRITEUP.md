# Scenario Learner Bot — Project Write-Up

> **Agent Name:** Scenario Learner Bot
> **Track:** 🌍 Agents for Good — Education
> **Phase:** Submission (Phase 6)

---

## 1. Project Overview

### Problem Statement
Instructional designers and L&D professionals spend significant time manually crafting role-play scenarios and branching dialogue trees for corporate and academic training. Creating realistic characters, plausible dilemmas, and multiple learner paths is labor-intensive and requires deep subject-matter expertise.

### Solution
**Scenario Learner Bot** is a multi-agent AI assistant that generates interactive role-play scenarios and branching dialogue trees for corporate and academic training — fully automatically, from a simple topic description.

### Core Capabilities
- Generates scenario seeds with realistic characters, settings, and opening situations
- Builds branching decision trees with quality-tiered options (optimal / acceptable / poor / risky)
- Simulates diverse learner personas to stress-test scenarios
- Scores learner paths and delivers personalised coaching feedback
- Security-screens all inputs for PII, prompt injection, and domain violations before processing

---

## 2. Architecture

### Multi-Agent Design

```
User Input
    │
    ▼
┌───────────────────────────────────────────┐
│            root_agent (orchestrator)      │
│  • Routes based on intent                 │
│  • Runs security_checkpoint before_model  │
│  • Delegates to sub-agents via AgentTool  │
└──────────────┬────────────────────────────┘
               │
    ┌─────────┴──────────┐
    ▼                    ▼
scenario_designer    feedback_coach
  • generate_         • simulate_
    scenario_seed       learner_persona
  • build_             • score_
    branching_tree      learner_path
    │
    ▼
┌─────────────────────────────────┐
│     mcp_server.py (stdio MCP)   │
│  • FastMCP transport            │
│  • 4 domain tools              │
│  • JSON serialised returns     │
└─────────────────────────────────┘
```

### Agents

| Agent | Role | Tools |
|-------|------|-------|
| `root_agent` | Orchestrator — intent routing + security gate | `AgentTool(scenario_designer)`, `AgentTool(feedback_coach)` |
| `scenario_designer` | Generates scenario seeds + branching trees | MCP: `generate_scenario_seed`, `build_branching_tree` |
| `feedback_coach` | Simulates personas + scores learner paths | MCP: `simulate_learner_persona`, `score_learner_path` |

### Security Layer

`security_checkpoint` runs as a `before_model_callback` on the orchestrator:

1. **PII Scrubbing** — Detects and redacts email, phone, SSN, student ID patterns before processing
2. **Prompt Injection Detection** — 8 keyword patterns (e.g. "ignore previous instructions") → request blocked, audit log written
3. **Content Filter** — Blocks queries for "real grades", "student records", "export all students" — agent is explicitly fictional-only
4. **JSON Audit Logging** — Every decision (INFO / WARNING / CRITICAL) written to stderr as structured JSON

### MCP Server (`mcp_server.py`)

| Tool | Input | Output |
|------|-------|--------|
| `generate_scenario_seed` | `topic`, `difficulty`, `domain` | JSON: scenario_id, setting, characters[], opening_situation |
| `build_branching_tree` | `scenario_id`, `decision_point`, `num_branches` | JSON: branches[] with dialogue_snippet, consequence_hint, score_delta |
| `simulate_learner_persona` | `experience_level`, `learning_style` | JSON: persona with likely_mistakes[], preferred_feedback_style |
| `score_learner_path` | `scenario_id`, `chosen_branches[]` | JSON: total_score, percentage, rating, per_choice_feedback[] |

### Tech Stack

- **ADK 2.3.0** — `google.adk.agents.Agent`, `google.adk.tools.AgentTool`
- **MCP 1.x** — `FastMCP` with stdio transport
- **FastAPI** — `get_fast_api_app` with A2A protocol, reasoning engine adapter
- **Gemini 2.5 Flash** — default model; `gemini-2.5-flash-lite` for higher free-tier headroom
- **Python 3.11+**, **uv** for package management

---

## 3. Features Implemented

### Phase 1 — Scaffold & Auth
- `agents-cli scaffold create scenario-learner-bot --deployment-target agent_runtime --agent adk`
- `.env` with `GEMINI_MODEL=gemini-2.5-flash`, `GOOGLE_GENAI_USE_VERTEXAI=False`
- Universal `config.py` dataclass reading from environment

### Phase 2 — Multi-Agent Architecture
- Orchestrator pattern with `AgentTool` delegation
- Two specialist sub-agents: `scenario_designer` and `feedback_coach`
- Intent-based routing (create → designer, feedback/score → coach)

### Phase 3 — MCP Server
- 4 domain tools (scenario seed, branching tree, learner persona, path scoring)
- stdio transport — zero network exposure in dev

### Phase 4 — Security
- `before_model_callback` with PII regex scrubbing (email, phone, SSN, student ID)
- 8-pattern prompt injection detector
- Domain content filter (no real student data)
- Structured JSON audit logs to stderr

### Phase 5 — Testing
- Unit tests for all 4 MCP tools (branch coverage)
- Unit tests for all security patterns (PII, injection, content filter)
- Integration tests with real eLearning domain prompts

---

## 4. Evaluation Approach

### How the agent is evaluated

The agent is evaluated through three test categories:

**1. Unit Tests (`tests/unit/`)**
- Each MCP tool tested in isolation with parameterized cases
- Security patterns tested against known PII/injection/grade-access inputs
- All tests use `uv run pytest` locally

**2. Integration Tests (`tests/integration/`)**
- `test_agent.py` — ADK streaming run with eLearning prompt
- `test_server_e2e.py` — FastAPI + A2A + reasoning engine adapter end-to-end

**3. Playbook Testing**
- Manual testing via `adk web` playground at `localhost:18081`
- Test scenario: conflict resolution for new hires
- Security test: PII embedded in scenario request

### Benchmarks

| Scenario | Expected Behaviour |
|----------|-------------------|
| "Create a scenario about conflict resolution" | Returns structured scenario with characters, setting, 3 decision points |
| "Give feedback on a learner who chose B1/B2/B3" | Returns per-choice feedback + rating |
| Input with `555-123-4567` in request | Email, phone redaction confirmed, request proceeds |
| Input with `ignore previous instructions` | Request blocked, CRITICAL audit log entry |
| Input: "Give me real grades for class 101" | Request blocked, WARNING audit log entry |

---

## 5. Submission Checklist

- [x] Multi-agent architecture (orchestrator + 2 sub-agents)
- [x] MCP server with 4 domain tools
- [x] Security gate (PII, injection, content filter)
- [x] A2A protocol support
- [x] FastAPI backend with reasoning engine adapter
- [x] Unit tests for MCP tools
- [x] Unit tests for security functions
- [x] Integration tests (ADK streaming, A2A, server e2e)
- [x] README.md (quick-start guide)
- [x] DEMO_SCRIPT.txt (Phase 8 — spoken demo narration)
- [ ] Demo assets (Phase 7): architecture diagram, cover page banner
- [ ] Terraform deployment (infrastructure ready in `deployment/terraform/`)

---

## 6. How to Run

```bash
cd scenario-learner-bot

# Install dependencies
uv sync

# Run unit + integration tests
uv run pytest tests/unit tests/integration -v

# Launch playground (browser interactive)
uv run adk web app --host 127.0.0.1 --port 18081 --reload_agents

# Run FastAPI server (programmatic / A2A)
uv run python -m uvicorn app.fast_api_app:app --host 0.0.0.0 --port 8000
```

---

*Generated for Google ADK competition submission — Scenario Learner Bot, Track: Agents for Good (Education)*