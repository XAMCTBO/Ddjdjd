# OBD AI diagnostics server

A self-hosted backend that adds AI diagnostics to the OBD Logger app. Instead of one general-purpose prompt, a
dispatcher routes each request to a small team of specialist agents. Each agent has a narrow job, its own prompt
and output schema, and only the data it needs.

```
 phone (obd-logger.html)                     ai-server
 ───────────────────────     raw ELM327      ┌────────────────────────────────────────────┐
  Scan codes ───────────────────────────────▶│ Orchestrator (routing · tiers · limits ·   │
  Recording ────────────────────────────────▶│              shared session memory/SQLite) │
  Chat / Predict / Report ──────────────────▶│                                            │
                                             │  OBD Reader  →  DTC Analyzer → Recommender │
 web panel (/)  ────────────────────────────▶│  Prediction     Report         Chat        │
 MCP clients (/mcp) ────────────────────────▶│            ▲ RAG (knowledge base) ▲        │
                                             └────────────────────────────────────────────┘
```

| Agent | What it does | LLM? |
|---|---|---|
| **OBD Reader** (`agents/obd_reader.py`) | Decodes raw ELM327 text: about 50 Mode 01 PIDs, the readiness bitmap, freeze frames (Mode 02), stored/pending/permanent codes (03/07/0A), VIN (09), and ISO-TP multi-frame CAN responses, with spaces on or off. It detects the protocol from `ATDPN` and flags v2.1 clone adapters. | No, it's deterministic |
| **DTC Analyzer** (`agents/dtc_analyzer.py`) | Explains each code for this car: ranked likely causes with evidence from the freeze frame and live values, a diagnostic plan, recurring codes from earlier sessions, and known code combinations (e.g. P0300 + P0171 suggests an air leak). Brake and airbag codes can never be marked "safe". | Yes, with an offline fallback |
| **Recommendation** (`agents/recommendation.py`) | An action plan ordered cheapest first, adjusted to the user's DIY level and tools, with weather warnings (e.g. EVAP monitors don't run below about 4 °C). | Yes, with an offline fallback |
| **Prediction** (`agents/prediction.py`) | Reduces every recording to health metrics: warm fuel trims, warm-up time, cruise coolant temperature, charging voltage, O2 switching rate, and the catalyst ratio. It fits a robust trend (Theil–Sen) across sessions and projects days or km until each metric crosses a fault threshold. Needs 3 or more sessions. | Numbers are deterministic; the LLM only writes the summary |
| **Report Generator** (`agents/report.py`) | A self-contained HTML report with SVG charts, printable to PDF. Modes: `owner`, `mechanic`, and `sale` (a pre-purchase check that includes a "codes recently cleared?" test). Languages: English and Ukrainian. | No |
| **Chat** (`agents/chat.py`) | A conversational assistant that uses Claude tool calls (`lookup_dtc`, `search_knowledge`, `get_vehicle_context`, `suggest_screen`). It understands informal symptoms ("dies at the light", "smells like fuel"). | Yes, with an offline fallback |
| **RAG** (`agents/rag.py`) | BM25 retrieval over `knowledge/articles/*.md`, the DTC catalog, and code-combination patterns. Add your own notes or bulletins via `OBDAI_KB_DIRS`. | No |
| **Orchestrator** (`orchestrator.py`) | Routes requests (e.g. "What does P0420 mean?" goes straight to a catalog lookup with no model call), gates features by plan tier, enforces per-day limits, and stores every agent's output so later agents can read it. | No |

## Run it

```bash
cd ai-server
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...      # or run `ant auth login`
python -m obdai.server --port 8787 --db obdai.sqlite
```

Open `http://<server>:8787/`, click **Create account**, and copy the token. In the phone app's **AI diagnostics**
panel, enter the server address and that token, then **Scan codes**.

**Without an API key**, the server runs in *knowledge-base mode*. Everything still works, but the analysis,
recommendations, and chat come from the built-in catalog and guides instead of Claude. `GET /health` shows which
mode is active.

### Settings (environment variables)

| Variable | Default | Meaning |
|---|---|---|
| `OBDAI_MODEL` | `claude-opus-5-5` | Claude model used by all LLM agents |
| `OBDAI_EFFORT` | `medium` | Default effort. Chat runs at `low`; analysis at `medium`. |
| `OBDAI_DEFAULT_TIER` | `pro` | Tier for new accounts. Set `free` to get the freemium limits in `orchestrator.LIMITS` (10 chat messages a day; no predictions or reports). |
| `OBDAI_ADMIN_KEY` | unset | If set, creating an account requires `{"admin_key": ...}`. Use this when the server is reachable from the internet. |
| `OBDAI_KB_DIRS` | unset | Extra folders of `.md` files to add to the knowledge base |
| `OBDAI_OFFLINE` | unset | `1` forces knowledge-base mode |

### HTTPS

The Android app blocks plain `http://` (`usesCleartextTraffic="false"`), so it can only reach the server over
HTTPS. Put the server behind a reverse proxy with a certificate (Caddy, nginx), or a tunnel (Cloudflare Tunnel,
Tailscale Funnel). Plain HTTP works from a desktop browser for local testing.

## API

All endpoints except `/`, `/health`, `/api/register`, `/api/dtc/*` and `/api/search` need an
`Authorization: Bearer <token>` header (`?token=` also works, for opening reports in a browser).

| Method | Path | Notes |
|---|---|---|
| POST | `/api/register` | `{name}` → `{token}` |
| GET | `/api/me` | Profile, tier, and vehicles |
| POST | `/api/profile` | `{diy_level: none/beginner/intermediate/advanced, tools: [...]}` |
| POST | `/api/vehicles` | `{make, model, year, odometer_km, km_per_day}` |
| POST | `/api/scan` | `{raw: {ati, dpn, status, stored, pending, permanent, vin, supported, freeze, live}, vehicle, vehicle_id?, samples?}`. Runs OBD Reader, then DTC Analyzer, then Recommendation. |
| POST | `/api/recording` | `{vehicle_id, samples: [{t, rpm, speed, coolant, stft, ltft, voltage, maf, o2_b1s1, ...}]}` |
| GET | `/api/vehicles/{id}/sessions` | Session list, latest diagnosis, and recommendations |
| GET | `/api/vehicles/{id}/predictions` | Prediction agent |
| GET | `/api/vehicles/{id}/report?mode=owner\|mechanic\|sale&lang=en\|uk&session=` | HTML report |
| POST | `/api/vehicles/{id}/chat` | `{message}` → `{text, actions}` |
| GET | `/api/dtc/{code}` | Catalog lookup |
| GET | `/api/search?q=` | Knowledge-base search |
| POST | `/mcp` | MCP (JSON-RPC) endpoint, see below |

### Use it from Claude (MCP)

`/mcp` serves a minimal Model Context Protocol endpoint. Its tools are `decode_obd_response`, `lookup_dtc`,
`search_knowledge`, `analyze_codes`, `list_vehicles`, `vehicle_history`, and `predict_failures`. Add it to an MCP
client as an HTTP server at `https://<server>/mcp` with the header `Authorization: Bearer <token>`. You can then
ask Claude things like "look at my car's last three sessions and tell me what's trending".

## Tests

```bash
cd ai-server && python -m unittest discover -s tests -v
```

The tests run offline. The Claude code path is exercised with a fake client, so the suite never calls the API or
spends money. CI runs them on every push that touches `ai-server/`.

## Honest limitations

- **Generic OBD-II only.** Engine and emissions modules over standard modes. ABS, airbag, and body modules usually
  need manufacturer protocols, which this doesn't speak. The knowledge base explains B/C/U codes if another tool
  reads them.
- **The DTC catalog is hand-written**: about 100 common codes with causes and rough USD cost ranges, plus
  subsystem-level fallbacks for every other code. It isn't a licensed database of every manufacturer code.
- **Predictions compare the car with its own history** and with published thresholds. There's no fleet-wide
  dataset of other vehicles.
- Advice is a starting point, not a certified diagnosis. For brakes, steering, and airbags, the agents always point
  to a professional inspection.
