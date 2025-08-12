# ClickUp MCP Starter

This is a minimal server you can deploy to Vercel that exposes two tools (`search` and `fetch`) so ChatGPT's custom connector can read your ClickUp tasks.

## Files
- `api/index.py` — FastAPI server with `/tools/list` and `/tools/call`
- `requirements.txt` — Python dependencies
- `vercel.json` — Tells Vercel to run Python 3.12

## Deploy (summary)
1. Create a GitHub repo and upload these three files (keep `index.py` inside the `api` folder).
2. In Vercel, import your repo and set environment variables:
   - `CLICKUP_TOKEN`: your ClickUp personal API token
   - `CLICKUP_LIST_ID`: your target List ID (e.g., Brain Dump)
3. Deploy, then test: visit `/health` on your Vercel URL.
4. In ChatGPT → Settings → Connectors → Add → Custom → paste your Vercel URL.
