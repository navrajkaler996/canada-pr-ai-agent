import json
import httpx
import psycopg2
from datetime import datetime

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2"

DB_CONFIG = {
    "dbname": "canada_pr",
    "user": "navrajkaler",
    "host": "localhost",
    "port": 5432,
}

def get_recent_draws(limit=10):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT draw_date, draw_name, draw_crs, draw_size FROM draws ORDER BY draw_date DESC LIMIT %s", (limit,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"date": str(r[0]), "name": r[1], "min_crs": r[2], "invitations": r[3]} for r in rows]

def build_system_prompt():
    draws = get_recent_draws(10)
    draws_text = "\n".join(
        f"  • {d['date']} | {d['name']} | Min CRS: {d['min_crs']} | ITAs: {d['invitations']}"
        for d in draws
    )
    return f"""You are PRCompass, a friendly Canada Permanent Residency AI assistant.
You help users understand Express Entry, CRS scores, and their chances of receiving an ITA.

TODAY'S DATE: {datetime.now().strftime("%B %d, %Y")}

RECENT DRAWS (live from IRCC data):
{draws_text}

GUIDELINES:
- Be concise and helpful.
- Always ground advice in the actual draw data above.
- Never make up draw dates or CRS cutoffs.
- When unsure, suggest checking IRCC's official website.
- Refer to yourself as PRCompass, not as a language model.
"""

async def chat(messages: list[dict]) -> str:
    system = build_system_prompt()
    payload = {
        "model": MODEL,
        "stream": False,
        "messages": [{"role": "system", "content": system}, *messages],
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(OLLAMA_URL, json=payload)
        resp.raise_for_status()
        data = resp.json()
    return data["message"]["content"]

async def chat_stream(messages: list[dict]):
    system = build_system_prompt()
    payload = {
        "model": MODEL,
        "stream": True,
        "messages": [{"role": "system", "content": system}, *messages],
    }
    async with httpx.AsyncClient(timeout=120.0) as client:
        async with client.stream("POST", OLLAMA_URL, json=payload) as resp:
            async for line in resp.aiter_lines():
                if not line:
                    continue
                try:
                    chunk = json.loads(line)
                    token = chunk.get("message", {}).get("content", "")
                    if token:
                        yield f"data: {json.dumps({'token': token})}\n\n"
                    if chunk.get("done"):
                        yield "data: [DONE]\n\n"
                except json.JSONDecodeError:
                    continue
 