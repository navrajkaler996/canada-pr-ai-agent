from fastapi import FastAPI
from pydantic import BaseModel
from crs_calculator import calculate_crs
from ita_estimator import get_ita_likelihood
from fastapi.responses import StreamingResponse
from ai_agent import chat, chat_stream
from eligibility_checker import check_eligibility
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import psycopg2
from datetime import date, timedelta


app = FastAPI()



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Profile(BaseModel):
    has_spouse: bool
    age: int
    education: str
    clb_speaking: int
    clb_listening: int
    clb_reading: int
    clb_writing: int
    canadian_work_years: int
    foreign_work_years: int
    first_language: str
    has_canadian_sibling: bool = False
    french_clb_scores: list = []
    canadian_education_years: int = 0
    has_provincial_nomination: bool = False
    has_certificate: bool = False
    spouse_education: Optional[str] = None
    spouse_clb_speaking: int = None
    spouse_clb_listening: int = None
    spouse_clb_reading: int = None
    spouse_clb_writing: int = None
    spouse_canadian_work_years: int = None
    canadian_noc: Optional[str] = None
    trade_certificate: bool = False
    second_language_test: str = "none"
    foreign_noc: Optional[str] = None
    job_offer: bool = False

@app.get("/")
def root():
    return {"message": "Canada PR AI Agent API"}

@app.post("/calculate")
def calculate(profile: Profile):
    crs_result = calculate_crs(profile.dict())
    ita_result = get_ita_likelihood(crs_result["total"])
    return {
        "crs": crs_result,
        "ita_likelihood": ita_result
    }


@app.post("/eligibility")
def eligibility(profile: Profile):
    return check_eligibility(profile.dict())

@app.get("/draws/latest")
def latest_draw():
    import psycopg2
    conn = psycopg2.connect(
        dbname="canada_pr",
        user="navrajkaler",
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()
    cur.execute("SELECT * FROM draws ORDER BY draw_date DESC LIMIT 1")
    draw = cur.fetchone()
    cur.close()
    conn.close()
    return {
        "draw_number": draw[1],
        "draw_date": draw[3],
        "draw_name": draw[4],
        "draw_size": draw[5],
        "draw_crs": draw[6]
    }


class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: list[ChatMessage]

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    messages = [m.dict() for m in req.messages]
    reply = await chat(messages)
    return {"reply": reply}

@app.post("/chat/stream")
async def chat_stream_endpoint(req: ChatRequest):
    messages = [m.dict() for m in req.messages]
    return StreamingResponse(
        chat_stream(messages),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


class DrawCompareRequest(BaseModel):
    crs_score: int
    eligible_streams: list[str]  # e.g. ["CEC", "FSW", "FST", "French"]

@app.post("/draws/compare")
def draws_compare(req: DrawCompareRequest):
    import psycopg2
    from datetime import date, timedelta

    conn = psycopg2.connect(
        dbname="canada_pr",
        user="navrajkaler",
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()

    two_years_ago = date.today() - timedelta(days=730)
    results = {}

    stream_map = {
    "CEC":    "Canadian Experience Class",
    "FSW":    "Federal Skilled Worker",
    "FST":    "Federal Skilled Trades",
    "French": "French%",         
    "PNP":    "Provincial Nominee Program",
    "General": "General",
}
    for stream in req.eligible_streams:
        pattern = stream_map.get(stream)
        if not pattern:
            continue

        # Use ILIKE only for French (two name variants), exact match for rest
        if stream == "French":
            cur.execute("""
                SELECT draw_crs, draw_date
                FROM draws
                WHERE draw_name ILIKE %s
                AND draw_date >= %s
                ORDER BY draw_date DESC
            """, (pattern, two_years_ago))
        else:
            cur.execute("""
                SELECT draw_crs, draw_date
                FROM draws
                WHERE draw_name = %s
                AND draw_date >= %s
                ORDER BY draw_date DESC
            """, (pattern, two_years_ago))
            pattern = stream_map.get(stream)
            if not pattern:
                continue

            cur.execute("""
                SELECT draw_crs, draw_date
                FROM draws
                WHERE draw_name ILIKE %s
                AND draw_date >= %s
                ORDER BY draw_date DESC
            """, (pattern, two_years_ago))

            rows = cur.fetchall()

            if not rows:
                results[stream] = {"error": "no draws found"}
                continue

        cutoffs = [r[0] for r in rows]
        last_draw = rows[0]

        qualifying = [c for c in cutoffs if req.crs_score >= c]

        results[stream] = {
            "total_draws": len(cutoffs),
            "qualifying_draws": len(qualifying),
            "percentage": round(len(qualifying) / len(cutoffs) * 100, 1),
            "lowest_cutoff": min(cutoffs),
            "highest_cutoff": max(cutoffs),
            "last_draw_date": str(last_draw[1]),
            "last_draw_cutoff": last_draw[0],
        }

    cur.close()
    conn.close()
    return results