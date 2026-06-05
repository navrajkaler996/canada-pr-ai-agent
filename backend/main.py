from fastapi import FastAPI
from pydantic import BaseModel
from crs_calculator import calculate_crs
from ita_estimator import get_ita_likelihood

app = FastAPI()

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
    spouse_education: str = None
    spouse_clb_speaking: int = None
    spouse_clb_listening: int = None
    spouse_clb_reading: int = None
    spouse_clb_writing: int = None
    spouse_canadian_work_years: int = None

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