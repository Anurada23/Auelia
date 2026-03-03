# Auelia — Multi-Agent AI Hotel Discovery & Automation System

An end-to-end AI-powered hotel discovery system combining a multi-agent LangGraph pipeline, real-time Amadeus GDS API integration, n8n workflow automation, and Snowflake data persistence.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM Inference | Groq (`llama-3.3-70b-versatile`) |
| Agent Orchestration | LangGraph + LangChain |
| Backend | FastAPI + Uvicorn |
| Hotel Data | Amadeus Self-Service GDS API |
| Workflow Automation | n8n |
| Database | Snowflake |
| Frontend | HTML + CSS + Vanilla JS |

---

## Project Structure

```
Auelia 2.0/
├── agents/
│   ├── memory.py               # Session context retrieval
│   ├── planner.py              # Research strategy via LLM
│   ├── researcher.py           # Direct Amadeus tool execution
│   ├── synthesizer.py          # Response formatting
│   └── prompts.py              # Agent system prompts
├── api/
│   ├── app.py                  # FastAPI app initialization
│   ├── hotel_routes.py         # Search + verify + verify-direct endpoints
│   └── schemas.py              # Pydantic request/response models
├── config/
│   ├── settings.py             # Environment variables
│   └── prompts.py              # System prompts
├── database/
│   ├── snowflake_client.py     # Snowflake connection
│   └── queries.py              # SQL statements
├── memory/
│   ├── conversation_memory.py  # In-memory session store
│   └── context_manager.py      # Context retrieval logic
├── n8n/
│   └── hotel-booking-workflow.json  # Import this into n8n UI
├── tools/
│   ├── amadeus_tool.py         # Amadeus search + verify functions
│   ├── search_tool.py          # Web search tool
│   └── visit_website.py        # Website content extraction
├── workflows/
│   ├── graph_builder.py        # LangGraph StateGraph definition
│   └── state.py                # WorkflowState TypedDict
├── frontend/
│   ├── hotel.html              # Main hotel discovery UI
│   └── hotel.js                # Card rendering + verify handler
├── tests/
├── .env                        # Environment variables (not committed)
├── requirements.txt
└── main.py
```

---

## Setup

### 1. Clone & Install

```bash
git clone <repo-url>


python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Mac/Linux

pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the root:

```env
# Groq
GROQ_API_KEY=your_groq_api_key

# Amadeus (sandbox)
AMADEUS_API_KEY=your_amadeus_client_id
AMADEUS_API_SECRET=your_amadeus_client_secret

# Snowflake
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_DATABASE=FINDER_AI
SNOWFLAKE_SCHEMA=PUBLIC
SNOWFLAKE_WAREHOUSE=COMPUTE_WH

# App
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true
```

### 3. API Keys

**Groq** — [console.groq.com](https://console.groq.com) → API Keys

**Amadeus** — [developers.amadeus.com](https://developers.amadeus.com) → Self-Service → Create App
- Client ID → `AMADEUS_API_KEY`
- Client Secret → `AMADEUS_API_SECRET`
- Sandbox environment used by default (`test.api.amadeus.com`)

**Snowflake** — [snowflake.com](https://snowflake.com) → Free trial. Tables auto-initialized on startup.

### 4. Run the Backend

```bash
python main.py
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### 5. Run n8n (separate terminal — no venv)

```bash
npx n8n
# or
npm install -g n8n && n8n start
# UI: http://localhost:5678
```

**Import the workflow:**
1. Open `http://localhost:5678`
2. New Workflow → `...` → Import from file → select `n8n/hotel-booking-workflow.json`
3. Connect Google account on the Google Sheets node
4. Replace `YOUR_GOOGLE_SHEETS_ID` with your sheet ID
5. Click **Activate**

### 6. Open Frontend

Open `frontend/hotel.html` in your browser.

---

## How It Works

### Hotel Search

```
1. User fills form → destination, dates, budget, preferences
2. POST /api/v2/hotels/search
3. FastAPI builds natural language query
4. LangGraph pipeline:
   Memory    → retrieves past session context
   Planner   → generates structured research plan
   Researcher → calls Amadeus API directly in Python
   Synthesizer → formats bullet lines preserving Hotel IDs
5. Frontend renders 5 hotel cards
```

### Real-Time Verification via n8n

```
1. User clicks "Check Live Price"
2. POST /api/v2/hotels/verify
3. FastAPI → POST → n8n webhook
4. n8n: Parse → /verify-direct → Compare Price → Google Sheets → Respond
5. Card expands inline:
   ✓ Available
   ↓ $X.XX — Price dropped!
   ⚡ Verified via n8n Automation
   [View & Book →]  [Select This Hotel]
```

> **Note:** n8n calls `/verify-direct` (not `/verify`) to prevent a circular call loop.
> Frontend → `/verify` → n8n → `/verify-direct` → Amadeus

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v2/hotels/search` | Multi-agent hotel discovery |
| `POST` | `/api/v2/hotels/verify` | Real-time verify via n8n |
| `POST` | `/api/v2/hotels/verify-direct` | Direct Amadeus verify (n8n only) |
| `POST` | `/api/v2/hotels/compare` | Price comparison |
| `GET`  | `/api/v2/hotels/searches/{session_id}` | Session search history |
| `GET`  | `/api/v2/health` | Health check |

---

## Multi-Agent Pipeline

### Memory Agent
Retrieves conversation history for the current session. Provides past search context to downstream agents. Saves each interaction after the workflow completes, feeding a cross-session preference loop back into future Memory retrievals.

### Planner Agent
Takes the natural language query and generates a structured research plan using `llama-3.3-70b-versatile` via Groq. Extracts city, dates, budget, and guest count.

### Researcher Agent
Calls `search_hotels_amadeus` **directly in Python** — the LLM is completely removed from data retrieval. Extracts parameters via regex, then calls:
- Amadeus OAuth token
- City IATA code lookup
- Hotel IDs by city (4–5 star)
- Live offers with pricing filtered by budget

Returns top ~5 as bullet lines with Hotel IDs required for verification.

### Synthesizer Agent
Strict passthrough for hotel data — preserves exact bullet format and Hotel IDs without reformatting. Configured to prevent the LLM from rewriting results as numbered lists, tables, or adding hallucinated citations.

---

## n8n Workflow

| Node | Type | Purpose |
|------|------|---------|
| Hotel Verify Webhook | Webhook | Receives request from FastAPI |
| Parse Request | Code | Validates and normalizes payload |
| Call Amadeus Verify | HTTP Request | POST to `/verify-direct` |
| Compare Price | Code | Detects price change vs original |
| Respond to Webhook | Respond | Returns result to FastAPI |

---

## Key Engineering Decisions

**Separate `/verify-direct` endpoint**
Prevents a circular call loop. `/verify` triggers n8n. `/verify-direct` is called by n8n only and goes straight to Amadeus. Clean separation avoids infinite recursion.

**Non-blocking Snowflake writes**
All database writes use FastAPI `BackgroundTasks` — Snowflake persistence happens after the response is already returned to the frontend, keeping API response times fast.

**Token overflow prevention**
Replaced `visit_website` scraping (8K TPM overflow, 403/429 bot-blocking) with structured Amadeus API responses. Combined with recursion limits and Top-5 result capping.

---

## Performance

| Metric | Before | After |
|--------|--------|-------|
| Response time | ~2 minutes | ~10 seconds |
| Improvement | — | ~92% faster |
| Tool call failures | Frequent (403/429) | None |
| Hallucination rate | High | Zero |
| Token overflow | Frequent | Never |
| Duplicate tool calls | 3–5 per query | 1 per query |

---

## Known Limitations

- Amadeus sandbox — not all hotels available for all date combinations
- Hotel IDs only present when Amadeus returns structured data
- Google Sheets node requires manual credential setup in n8n
- n8n must be running locally — fallback to direct Amadeus if unreachable

---

## Future Improvements

- Telegram bot via n8n for price drop push notifications
- Cron job price tracking — monitor saved hotels, alert on changes
- Structured LLM output for relative date parsing
- Production Amadeus environment for full global inventory

---

## License

MIT# Auelia - Hotel Booking System

A powerful multi-agent AI research assistant with **hotel booking capabilities** built with LangChain, LangGraph, Groq, FastAPI, and Snowflake.


## Architecture

```
User → Frontend → FastAPI → LangGraph Workflow
                              ├── Memory Agent (context)
                              ├── Planner Agent (strategy)
                              ├── Researcher Agent (search & scrape)
                              └── Synthesizer Agent (final answer)
                              
Results → Snowflake Storage → n8n Follow-up Tasks
```


## 🚀 Installation

### 1. Clone the repository

```bash
git clone <"https://github.com/Anurada23/Finder-2.0">
cd finder-ai-v2
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env` and fill in your credentials:

```bash
# API Keys
GROQ_API_KEY=your_groq_api_key_here

# Snowflake Configuration
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_DATABASE=FINDER_AI
SNOWFLAKE_SCHEMA=PUBLIC
SNOWFLAKE_WAREHOUSE=COMPUTE_WH

# Application Settings
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
```

### 5. Run the application

```bash
# Start the API server
python api/app.py

# Or using uvicorn directly
uvicorn api.app:app --reload --host 0.0.0.0 --port 8000
```

### 6. Open the frontend

Open `frontend/index.html` in your browser or serve it using:

```bash
cd frontend
python -m http.server 3000
```

Then visit: `http://localhost:3000`

## 📚 API Endpoints

### Health Check
```bash
GET /api/v2/health
```

### Research
```bash
POST /api/v2/research
Content-Type: application/json

{
  "query": "What are the latest developments in AI?",
  "session_id": "optional-session-id"
}
```

### Webhook (for n8n)
```bash
POST /api/v2/webhook
Content-Type: application/json

{
  "query": "Your research query",
  "session_id": "optional",
  "metadata": {}
}
```

### Get History
```bash
GET /api/v2/history/{session_id}
```

### Clear History
```bash
DELETE /api/v2/history/{session_id}
```

## 🔧 Configuration

### Agent Prompts

Edit agent behavior in `config/prompts.py`

### Settings

Adjust application settings in `config/settings.py`

### Memory

Configure memory limits in `.env`:
```
MAX_CONVERSATION_HISTORY=10
SESSION_TIMEOUT_MINUTES=30
```

## 🗄️ Snowflake Setup

### 1. Create Database

```sql
CREATE DATABASE FINDER_AI;
USE DATABASE FINDER_AI;
CREATE SCHEMA PUBLIC;
```

### 2. Tables are auto-created on startup

The application automatically creates:
- `research_sessions` - Main research data
- `conversation_history` - Chat history
- `agent_traces` - Agent execution logs

## 🔗 n8n Integration

### Setup Webhook in n8n

1. Create new workflow in n8n
2. Add "Webhook" node
3. Set Method: POST
4. Set Path: `/finder-webhook`
5. Add "HTTP Request" node
6. Configure:
   - Method: POST
   - URL: `http://your-api:8000/api/v2/webhook`
   - Body: JSON
   ```json
   {
     "query": "{{$json.query}}",
     "session_id": "{{$json.session_id}}"
   }
   ```

### Follow-up Tasks Examples

After receiving response, you can:

1. **Save to Google Sheets**
   - Add Google Sheets node
   - Map response data to columns

2. **Send Email Summary**
   - Add Gmail/SendGrid node
   - Include research findings

3. **Trigger Additional Research**
   - Add conditional logic
   - Loop back if incomplete

4. **Store in Database**
   - Add database node (MySQL, Postgres)
   - Save structured data

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Test specific module
pytest tests/test_agents.py

# With coverage
pytest --cov=. tests/
```

## 📁 Project Structure

```
finder-ai-v2/
├── agents/           # AI agents
├── api/              # FastAPI application
├── config/           # Configuration
├── database/         # Snowflake integration
├── frontend/         # Web interface
├── memory/           # Context management
├── tools/            # Agent tools
├── utils/            # Utilities
├── workflows/        # LangGraph workflows
├── .env              # Environment variables
└── requirements.txt  # Dependencies
```

## 🐛 Troubleshooting

### API Not Connecting
- Check if server is running: `curl http://localhost:8000/api/v2/health`
- Verify GROQ_API_KEY is set
- Check firewall settings

### Snowflake Connection Failed
- Verify credentials in `.env`
- Check network access to Snowflake
- Application will work without Snowflake (memory-only mode)

### Frontend Not Loading
- Check CORS settings in `api/app.py`
- Verify API URL in `frontend/js/api.js`
- Check browser console for errors

## 🔐 Security Notes

- Never commit `.env` file
- Use environment variables in production
- Implement rate limiting for production
- Add authentication for public deployment

## 📈 Performance Tips

- Adjust `MAX_CONVERSATION_HISTORY` based on needs
- Use Snowflake for long-term storage
- Implement caching for frequent queries
- Monitor API token usage


## 📄 License

MIT License - See LICENSE file

## 👥 Authors

Anuradha Senaratne

---
