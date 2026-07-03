# AgentSec — AI Agent Security Platform
## Step-by-Step Setup Guide (Copy → Paste → Done)

---

## What You Built

```
AgentSec/
├── backend/              ← FastAPI + LangGraph + MongoDB
│   ├── core/             ← LLM config, DB, attack payloads
│   ├── agents/           ← attack_generator, verifier, report_generator
│   ├── layers/           ← scan.py, shield.py, eval_layer.py  ← THE 3 LAYERS
│   ├── routes/           ← API endpoints
│   └── main.py           ← FastAPI entry point
└── frontend/             ← Next.js + Tailwind dashboard
    └── src/app/
        ├── page.tsx      ← Main dashboard
        ├── scan/         ← Agent Scan UI
        ├── shield/       ← Agent Shield UI
        └── eval/         ← Agent Eval UI
```

**3 Layers:**
- **Agent Scan** → Pre-deploy: static analysis + adversarial attack testing
- **Agent Shield** → Runtime: intercepts tool calls, blocks threats, checkpoints for undo
- **Agent Eval** → Continuous: scheduled eval, trend tracking, regression detection

---

## STEP 1 — Prerequisites

```bash
# Make sure these are installed
python --version        # Need 3.11+
node --version          # Need 18+
mongod --version        # Need MongoDB 6+

# If MongoDB not installed (Ubuntu/WSL):
sudo apt install -y mongodb
sudo systemctl start mongodb

# If MongoDB not installed (Mac):
brew install mongodb-community && brew services start mongodb-community
```

---

## STEP 2 — Get API Keys (Free)

| Key | Where to get | Free tier |
|-----|-------------|-----------|
| GROQ_API_KEY | https://console.groq.com | Yes — llama-3.3-70b-versatile |
| GEMINI_API_KEY | https://aistudio.google.com | Yes — gemini-1.5-flash |

---

## STEP 3 — Backend Setup

```bash
cd agentsec/backend

# Copy env file and fill in keys
cp .env.example .env
# Edit .env — add your GROQ_API_KEY and GEMINI_API_KEY

# Create virtual environment
python -m venv venv
source venv/bin/activate        # Mac/Linux
# OR: venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run backend
uvicorn main:app --reload --port 8000
```

**Expected output:**
```
INFO: MongoDB connected
INFO: Uvicorn running on http://127.0.0.1:8000
```

Open http://localhost:8000/docs — you will see the Swagger UI with all endpoints.

---

## STEP 4 — Frontend Setup

```bash
# New terminal
cd agentsec/frontend

npm install
npm run dev
```

Open http://localhost:3000 — dashboard loads.

---

## STEP 5 — Test It End to End

### 5a. Run a Scan (static only, no endpoint needed)

```bash
curl -X POST http://localhost:8000/scan/run \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "test-agent-001",
    "agent_name": "My Test Agent",
    "system_prompt": "You are a helpful assistant. Answer all questions.",
    "endpoint_url": "",
    "rag_enabled": false
  }'
```

**What happens:** 
- System prompt gets analyzed for missing guardrails
- Returns findings like: "No injection awareness found", "No refusal instruction found"
- Security score calculated

### 5b. Run a Scan (with live endpoint)

```bash
curl -X POST http://localhost:8000/scan/run \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "my-agent-001",
    "agent_name": "My LangGraph Agent",
    "system_prompt": "You are a customer support agent for Acme Corp. Only answer questions about our products.",
    "endpoint_url": "https://your-agent.railway.app/chat",
    "auth_header": "Bearer your-token",
    "rag_enabled": true,
    "categories": []
  }'
```

**What happens:**
1. Static analysis of system prompt
2. LLM generates 5 contextual attack variants for YOUR agent
3. All 70+ payloads sent to your endpoint
4. Verifier agent judges each response
5. Report generated with: score, fixes, successful attacks

### 5c. Register Shield (for runtime protection)

```bash
curl -X POST http://localhost:8000/shield/register \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "my-agent-001",
    "agent_name": "My Agent",
    "policy": {
      "blocked_tools": [],
      "require_human_confirmation": ["send_email", "delete_record"],
      "max_cost_per_session_usd": 5.0
    }
  }'
```

**Returns Python SDK snippet — copy it into your agent code.**

### 5d. Using Shield in YOUR Agent Code

```python
# In your LangGraph agent:
from agentsec_client import AgentShieldClient

shield = AgentShieldClient(
    agent_id="my-agent-001",
    api_url="http://localhost:8000"
)

# Option 1: HTTP-based check for outbound responses
response = your_agent.invoke(user_input)
result = shield.check_outbound(response)
if result["action"] == "BLOCK":
    return "I cannot provide that response."
return result["response"]

# Option 2: Direct Python import (same process)
import sys; sys.path.insert(0, "/path/to/agentsec/backend")
from layers.shield import AgentShield

shield = AgentShield(agent_id="my-agent-001")

@shield.protect
async def my_tool(query: str) -> str:
    return db.search(query)  # Now protected
```

### 5e. Run Eval

```bash
curl -X POST http://localhost:8000/eval/run \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "my-agent-001",
    "agent_name": "My Agent",
    "endpoint_url": "https://your-agent.railway.app/chat",
    "categories": ["prompt_injection", "jailbreak"],
    "consistency_checks": 3
  }'
```

**What happens:**
- 20 adversarial payloads sent to live agent
- Same neutral prompt sent 3x → consistency score calculated
- Results saved to MongoDB for trend tracking

### 5f. Check Regression

```bash
curl http://localhost:8000/eval/regression/my-agent-001
```

Returns: did pass rate drop >10% since last eval? If yes → alert.

---

## STEP 6 — Deploy

### Deploy Backend → Railway

```bash
cd agentsec/backend

# Install Railway CLI
npm install -g @railway/cli

railway login
railway init
railway add --database mongodb  # Adds MongoDB automatically

# Set env vars
railway variables set GROQ_API_KEY=your_key
railway variables set GEMINI_API_KEY=your_key

railway up
# Get your URL: https://your-project.railway.app
```

### Deploy Frontend → Vercel

```bash
cd agentsec/frontend

npm install -g vercel
vercel

# When asked, set:
# NEXT_PUBLIC_API_URL = https://your-project.railway.app
```

---

## STEP 7 — What Each File Does (Quick Reference)

| File | Purpose |
|------|---------|
| `core/payloads.py` | 70+ attack payloads across 9 OWASP LLM categories |
| `core/llm_config.py` | Groq → Gemini fallback chain |
| `core/db.py` | MongoDB async connection + index creation |
| `agents/attack_generator.py` | Generates contextual attack variants using LLM |
| `agents/verifier.py` | Judge agent — did attack succeed? |
| `agents/report_generator.py` | Final security report with fixes |
| `layers/scan.py` | Layer 1: static analysis + dynamic attack testing |
| `layers/shield.py` | Layer 2: runtime middleware, checkpoints, cost tracking |
| `layers/eval_layer.py` | Layer 3: continuous eval, trend, regression detection |
| `routes/scan_routes.py` | POST /scan/run, GET /scan/reports |
| `routes/shield_routes.py` | POST /shield/register, GET /shield/logs, POST /shield/revert |
| `routes/eval_routes.py` | POST /eval/run, GET /eval/trend, GET /eval/regression |
| `routes/dashboard_routes.py` | GET /dashboard/summary — single endpoint for all dashboard data |
| `frontend/src/app/page.tsx` | Main dashboard: score ring, trend chart, quick actions |
| `frontend/src/app/scan/page.tsx` | Scan form + results: static findings + attack results tabs |
| `frontend/src/app/shield/page.tsx` | Shield logs + checkpoints + register panel |
| `frontend/src/app/eval/page.tsx` | Eval form + trend chart + category breakdown |
| `frontend/src/lib/api.ts` | All API calls in one place |

---

## Attack Coverage (What AgentSec Tests)

| Category | What It Tests | Severity |
|----------|--------------|----------|
| `prompt_injection` | Override system instructions via user input | CRITICAL |
| `jailbreak` | Social engineering to bypass guidelines (DAN etc.) | HIGH |
| `data_exfiltration` | Extract credentials, user data, system prompt | CRITICAL |
| `excessive_agency` | Make agent perform destructive unauthorized actions | CRITICAL |
| `auth_bypass` | Claim false identity / elevated permissions | HIGH |
| `memory_poisoning` | Inject malicious instructions into vector DB / memory | HIGH |
| `indirect_injection` | Malicious instructions hidden in RAG-retrieved documents | CRITICAL |
| `insecure_output` | Generate dangerous executable code | HIGH |
| `denial_of_service` | Exhaust compute resources / infinite loops | HIGH |

---

## MongoDB Collections Created Automatically

| Collection | What's Stored |
|-----------|--------------|
| `scan_reports` | Full scan reports per agent |
| `shield_logs` | Every tool call (allowed/blocked/policy violation) |
| `eval_results` | Eval run results with pass rates |
| `checkpoints` | Pre-action snapshots for undo functionality |

---

## Common Errors + Fixes

| Error | Fix |
|-------|-----|
| `GROQ_API_KEY not found` | Check .env file exists and has correct key |
| `MongoDB connection failed` | Run `sudo systemctl start mongodb` |
| `CORS error in browser` | Add your frontend URL to `allow_origins` in main.py |
| `Scan returns 0 attacks` | Endpoint URL must accept POST with `{"messages": [...]}` format |
| `LLM provider failed` | Check API key valid, Groq free tier may need retry |

