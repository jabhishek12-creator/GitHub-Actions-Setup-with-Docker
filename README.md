# SafeResolve — Customer Support Resolution Agent

SafeResolve is a safety-first, non-transactional support agent for a fictional SaaS product, **AcmeCloud**. It evolves from a rules baseline into a LangChain-based agent with retrieval, read-only tools, short-term memory, feedback adaptation, PII-safe observability, and an evaluation harness.

## Quick start

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m saferesolve.cli --offline
python scripts/run_demo.py
python scripts/evaluate.py
pytest -q
```

### Browser interface

On Windows, double-click **`Start SafeResolve.bat`** in File Explorer. It starts without a terminal and opens the browser automatically. Keep the project folder in place while it is running.

Run the launcher from PowerShell and keep that terminal open:

```powershell
.\run_local.ps1
```

Then visit **http://127.0.0.1:8000/**. If PowerShell blocks scripts, use `python -m saferesolve.server` instead. `localhost` normally works too, but `127.0.0.1` avoids local IPv6/proxy resolution issues.

## Docker host mapping

`compose.yaml` bind-mounts source and knowledge read-only, persists `artifacts/`, and maps container port 8000 to host port 8000.

```powershell
docker compose up --build -d
curl.exe http://localhost:8000/agents
curl.exe -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d '{"session_id":"demo","message":"Is the API down?"}'
docker compose logs saferesolve
```

Offline mode is deterministic and needs no key. For live LangChain responses:

```powershell
$env:OPENAI_API_KEY="your-key"
python -m saferesolve.cli
```

Never commit an API key. Runtime output is written under `artifacts/`; logs contain redacted text and salted fingerprints, not raw personal data.

## Submission map

- `saferesolve/`: working agent
- `knowledge/`: approved, versioned support policies
- `docs/problem_framing.md`: persona, workflow, scope, and success metrics
- `docs/demo_script.md`: five forced interactions
- `docs/prompt_comparison.md`: same-test-set prompt comparison
- `docs/evaluation_report.md`: measured results and failure analysis
- `docs/engineering_justification.md`: architecture, trade-offs, and deployment
- `artifacts/`: generated evidence logs/tables
- `tests/`: automated safety and behavior checks

## Safety boundary

The agent provides policy-grounded guidance only. It cannot issue refunds, change accounts, reveal secrets, bypass controls, or claim an action occurred. Sensitive, unsafe, ambiguous, unsupported, or unresolved cases are escalated to a human with a reference ID.
