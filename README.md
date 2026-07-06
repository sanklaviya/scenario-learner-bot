# Scenario Learner Bot

**Generates interactive role-play scenarios and branching dialogue trees for corporate and academic training — powered by a multi-agent architecture with Gemini.**

🌍 **Track:** Agents for Good — Education

---

## What It Does

You describe a training topic (e.g. *"conflict resolution for new hires"*), and the agent generates:

1. A **scenario seed** with realistic characters, a setting, and an opening situation
2. A **branching decision tree** with 2–4 options per decision point (optimal / acceptable / poor / risky)
3. **Learner persona simulations** to stress-test the scenario
4. **Personalised feedback** scoring the learner's choices

All inputs are screened for PII, prompt injection, and misuse before processing.

---

## Architecture

```
root_agent (orchestrator + security gate)
    ├── scenario_designer ──→ MCP: generate_scenario_seed, build_branching_tree
    └── feedback_coach ─────→ MCP: simulate_learner_persona, score_learner_path
        │
        ▼
mcp_server.py (FastMCP, stdio transport — 4 tools)
```

**Security:** `before_model_callback` screens all inputs (PII redaction, injection detection, content filter).

---

## Quick Start

### 1. Install dependencies

```bash
cd scenario-learner-bot
uv sync
```

### 2. Add your API key

Edit `.env` and replace `<paste_your_key_here>` with your Gemini API key from [aistudio.google.com/apikey](https://aistudio.google.com/apikey):

```env
GOOGLE_API_KEY=<your-key>
GOOGLE_GENAI_USE_VERTEXAI=False
GEMINI_MODEL=gemini-2.5-flash
```

### 3. Run the playground (browser UI)

```bash
uv run adk web app --host 127.0.0.1 --port 18081 --reload_agents
```

Open [http://localhost:18081](http://localhost:18081) in your browser.

### 4. Run the FastAPI server (programmatic / A2A)

```bash
uv run python -m uvicorn app.fast_api_app:app --host 0.0.0.0 --port 8000
```

---

## Try These Prompts

### Create a scenario
> "Create a training scenario about conflict resolution for new hires in a corporate setting"

### Create an academic scenario
> "Build an academic scenario about ethical research practices for graduate students"

### Get learner feedback
> "Score this learner's choices: SCN-1234-B1, SCN-1234-B2, SCN-1234-B3, SCN-1234-B1"

### Test the security filter
> Paste a message containing an email or phone number and ask it to create a scenario — the PII will be redacted and logged.

---

## Running Tests

```bash
# Unit tests (MCP tools + security)
uv run pytest tests/unit -v

# Integration tests (ADK streaming + A2A + server e2e)
uv run pytest tests/integration -v

# All tests
uv run pytest tests/ -v
```

---

## File Structure

```
scenario-learner-bot/
├── app/
│   ├── agent.py              # root_agent + scenario_designer + feedback_coach
│   ├── mcp_server.py        # 4 MCP tools (FastMCP, stdio)
│   ├── config.py            # Gemini model + security settings
│   └── fast_api_app.py      # FastAPI + A2A + reasoning engine adapter
├── tests/
│   ├── unit/               # MCP tool + security unit tests
│   └── integration/        # ADK streaming + server e2e tests
├── deployment/terraform/    # GCP infrastructure (ready to deploy)
├── SUBMISSION_WRITEUP.md   # Full project documentation
└── DEMO_SCRIPT.txt         # Spoken demo narration
```

---

## Key Features

| Feature | Implementation |
|---------|---------------|
| Multi-agent routing | `AgentTool` delegation from orchestrator to sub-agents |
| Branching dialogue trees | MCP `build_branching_tree` → quality-tiered options |
| Learner persona simulation | MCP `simulate_learner_persona` → persona-driven feedback |
| PII scrubbing | Regex patterns for email, phone, SSN, student ID |
| Prompt injection detection | 8-keyword blocklist with JSON audit log |
| Content filter | Blocks requests for real student data |
| A2A protocol | Native support via `attach_a2a_routes` |
| Reasoning engine adapter | `/api/stream_reasoning_engine` endpoint |

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `http://localhost:8000/run_sse` | POST | ADK streaming run |
| `http://localhost:8000/a2a/app/` | POST | A2A JSON-RPC streaming |
| `http://localhost:8000/a2a/app/.well-known/agent-card.json` | GET | A2A agent card |
| `http://localhost:8000/api/stream_reasoning_engine` | POST | Vertex AI reasoning engine |
| `http://localhost:8000/feedback` | POST | Collect learner feedback |

---

*Built with Google ADK 2.3.0 + FastMCP + Gemini 2.5 Flash*