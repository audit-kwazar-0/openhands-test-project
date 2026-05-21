# openhands-test-project

Test repo for the local OpenHands + DevOps RAG stack.

## Lab Sentinel

Health monitor: YAML config, SQLite, background poller, FastAPI, `labctl` CLI.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
bash scripts/setup-venv.sh
chmod +x labctl
./labctl init && ./labctl check && ./labctl status
.venv/bin/python -m lab_sentinel.main -c config/lab.yaml
```

API: `GET /health`, `/services`, `/checks`

```bash
.venv/bin/pytest -q
```

**Troubleshooting:** `ModuleNotFoundError: yaml` or `lab_sentinel` → in sandbox only: `bash scripts/setup-venv.sh`. Always `.venv/bin/pytest`, never system `pytest` or host pip.

### Agents: Tavily vs RAG

- **Tavily** needs `TAVILY_API_KEY` on the OpenHands server (see below). Without it, web search fails — that is expected locally.
- Use **devops-rag MCP** (`search_documentation`, `rag_status`) for stack/docs, not Tavily.
- Do not write Python via `echo` (breaks newlines). Use the file editor.

### Optional Tavily (web search)

1. Key: https://tavily.com (starts with `tvly-`)
2. Add to `docker-compose.yaml` under `openhands.environment`:
   `TAVILY_API_KEY=tvly-...`
3. `docker compose up -d openhands`

Or disable: tell the agent not to use web search; RAG + repo files are enough for Lab Sentinel.
