from fastapi import FastAPI, Request
import httpx, os
from typing import Dict, Any, List

app = FastAPI()

CLICKUP_TOKEN = os.environ.get("CLICKUP_TOKEN", "")
DEFAULT_LIST_ID = os.environ.get("CLICKUP_LIST_ID", "")

headers = {"Authorization": CLICKUP_TOKEN}

def _task_to_hit(t: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": t.get("id"),
        "title": t.get("name"),
        "snippet": (t.get("text_content") or t.get("description") or "")[:200],
        "url": f'https://app.clickup.com/t/{t.get("id")}',
        "status": (t.get("status") or {}).get("status"),
        "due_date": t.get("due_date"),
    }

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/tools/list")
async def list_tools():
    # Minimal MCP-style descriptor: expose 'search' and 'fetch' tools
    return {
        "tools": [
            {
                "name": "search",
                "description": "Search ClickUp tasks by simple text and/or filters",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "q": {"type": "string"},
                        "list_id": {"type": "string"},
                        "include_closed": {"type": "boolean"},
                        "page": {"type": "integer"}
                    },
                    "required": []
                }
            },
            {
                "name": "fetch",
                "description": "Fetch full details for a set of task IDs",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "ids": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["ids"]
                }
            }
        ]
    }

@app.post("/tools/call")
async def call_tool(req: Request):
    body = await req.json()
    name = body.get("name")
    args = body.get("arguments", {}) or {}

    if name == "search":
        q = args.get("q", "").strip()
        list_id = args.get("list_id") or DEFAULT_LIST_ID
        include_closed = args.get("include_closed", False)
        page = int(args.get("page", 0))
        params = {
            "page": page,
            "include_closed": str(include_closed).lower()
        }
        # ClickUp 'Get Tasks' by list
        url = f"https://api.clickup.com/api/v2/list/{list_id}/task"
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.get(url, headers=headers, params=params)
            r.raise_for_status()
            data = r.json()
        tasks: List[Dict[str, Any]] = data.get("tasks", [])
        if q:
            q_lower = q.lower()
            tasks = [t for t in tasks if q_lower in (t.get("name","").lower() + (t.get("text_content") or "").lower())]
        hits = [_task_to_hit(t) for t in tasks[:25]]
        return {"content": hits}

    if name == "fetch":
        ids: List[str] = args["ids"]
        out = []
        async with httpx.AsyncClient(timeout=20) as client:
            for tid in ids:
                r = await client.get(f"https://api.clickup.com/api/v2/task/{tid}", headers=headers)
                r.raise_for_status()
                t = r.json()
                out.append({
                    "id": tid,
                    "title": t.get("name"),
                    "description": t.get("description"),
                    "status": (t.get("status") or {}).get("status"),
                    "due_date": t.get("due_date"),
                    "url": f"https://app.clickup.com/t/{tid}"
                })
        return {"content": out}

    return {"error": f"Unknown tool: {name}"}
