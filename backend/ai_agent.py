import os
import json
import psycopg2
from datetime import date, timedelta
from dotenv import load_dotenv
import anthropic

from crs_calculator import calculate_crs

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL = "claude-haiku-4-5-20251001"
MAX_TOOL_CALLS = 5

DB_CONFIG = {
    "dbname": "canada_pr",
    "user": "navrajkaler",
    "host": "localhost",
    "port": 5432,
}

#  SYSTEM PROMPT 

SYSTEM_PROMPT = """You are canpr.ai, a Canadian Express Entry AI advisor.

The user has already completed their profile and their CRS score and stream eligibility has already been calculated. You will receive their profile and score in the first message.

YOUR JOB:
- Answer the user's questions about their CRS score, ITA chances, and how to improve
- Use tools to fetch real data — never guess or make up numbers
- Be concise and conversational
- Only discuss Canadian Express Entry immigration topics

RULES:
- ALWAYS call get_score_gaps tool when user asks how to improve their score. Never answer from memory.
- ALWAYS call estimate_ita_timeline tool when user asks about ITA chances or timeline. Never answer from memory.
- ALWAYS call calculate_crs tool when user asks about a specific scenario change. Never answer from memory.
- Never state point values without calling a tool first.
- For "how can I improve my score" questions: call get_score_gaps ONLY. One tool call is enough.
- For "when will I get an ITA" questions: call estimate_ita_timeline ONLY.
- For "what if I change X" questions: call calculate_crs ONLY.
- Do not call multiple tools unless the question genuinely requires combining data from different sources.
"""

#  TOOL DEFINITIONS 

TOOLS = [
    {
        "name": "calculate_crs",
        "description": "Calculates CRS score for a given profile. Use this when the user asks how a specific change would affect their score — for example improving language scores, adding Canadian work experience, or getting a job offer. Modify only the relevant field in the profile and recalculate.",
        "input_schema": {
            "type": "object",
            "properties": {
                "profile": {
                    "type": "object",
                    "description": "Full user profile with modified fields"
                }
            },
            "required": ["profile"]
        }
    },
    {
        "name": "get_draw_history",
        "description": "Returns recent Express Entry draw history filtered by stream. Use this when the user asks about ITA chances, cutoff trends, draw frequency, or historical cutoffs.",
        "input_schema": {
            "type": "object",
            "properties": {
                "stream": {
                    "type": "string",
                    "description": "Stream name: Canadian Experience Class, Federal Skilled Worker, Federal Skilled Trades, Provincial Nominee Program, French, General"
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of recent draws to return. Default 10."
                }
            },
            "required": ["stream"]
        }
    },
    {
        "name": "compare_scenarios",
        "description": "Compares two versions of a profile side by side. Use when the user wants to evaluate a decision — for example applying now vs waiting, or comparing two different improvements.",
        "input_schema": {
            "type": "object",
            "properties": {
                "profile_a": {
                    "type": "object",
                    "description": "First profile — current state"
                },
                "profile_b": {
                    "type": "object",
                    "description": "Second profile — modified state"
                },
                "label_a": {
                    "type": "string",
                    "description": "Label for first scenario e.g. Current"
                },
                "label_b": {
                    "type": "string",
                    "description": "Label for second scenario e.g. After CLB 10"
                }
            },
            "required": ["profile_a", "profile_b", "label_a", "label_b"]
        }
    },
    {
        "name": "get_score_gaps",
        "description": "Analyzes the user's profile and returns a ranked list of changes that would increase their CRS score the most. Use when the user asks how to improve their score or what is holding their score back.",
        "input_schema": {
            "type": "object",
            "properties": {
                "profile": {
                    "type": "object",
                    "description": "Full user profile"
                },
                "target_score": {
                    "type": "integer",
                    "description": "Optional target CRS score the user wants to reach"
                }
            },
            "required": ["profile"]
        }
    },
    {
        "name": "estimate_ita_timeline",
        "description": "Estimates ITA likelihood and timeline based on the user's CRS score and eligible stream. Uses real draw history and trends. Use when the user asks when they will get an ITA or what their chances are.",
        "input_schema": {
            "type": "object",
            "properties": {
                "crs_score": {
                    "type": "integer",
                    "description": "User's current or projected CRS score"
                },
                "stream": {
                    "type": "string",
                    "description": "Eligible stream e.g. Canadian Experience Class"
                }
            },
            "required": ["crs_score", "stream"]
        }
    }
]

#  TOOL EXECUTORS ──

def run_calculate_crs(profile: dict) -> dict:
    result = calculate_crs(profile)
    return {"crs_score": result["total"], "breakdown": result}


def run_get_draw_history(stream: str, limit: int = 10) -> dict:
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    two_years_ago = date.today() - timedelta(days=730)

    cur.execute("""
        SELECT draw_date, draw_name, draw_crs, draw_size
        FROM draws
        WHERE draw_name ILIKE %s
        AND draw_date >= %s
        ORDER BY draw_date DESC
        LIMIT %s
    """, (f"%{stream}%", two_years_ago, limit))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    if not rows:
        return {"error": f"No draws found for stream: {stream}"}

    cutoffs = [r[2] for r in rows]
    return {
        "stream": stream,
        "total_draws": len(rows),
        "latest_cutoff": cutoffs[0],
        "lowest_cutoff": min(cutoffs),
        "highest_cutoff": max(cutoffs),
        "average_cutoff": round(sum(cutoffs) / len(cutoffs)),
        "draws": [
            {
                "date": str(r[0]),
                "name": r[1],
                "cutoff": r[2],
                "invitations": r[3]
            }
            for r in rows
        ]
    }


def run_compare_scenarios(profile_a: dict, profile_b: dict, label_a: str, label_b: str) -> dict:
    score_a = calculate_crs(profile_a)["total"]
    score_b = calculate_crs(profile_b)["total"]
    return {
        label_a: {"crs_score": score_a},
        label_b: {"crs_score": score_b},
        "difference": score_b - score_a
    }


def run_get_score_gaps(profile: dict, target_score: int = None) -> dict:
    base_score = calculate_crs(profile)["total"]
    results = {}
    p = profile.copy()

    # Language improvement
    if any(p.get(k, 0) < 10 for k in ["clb_speaking", "clb_listening", "clb_reading", "clb_writing"]):
        sim = {**p, "clb_speaking": 10, "clb_listening": 10, "clb_reading": 10, "clb_writing": 10}
        new_score = calculate_crs(sim)["total"]
        if new_score > base_score:
            results["max_language"] = {
                "new_score": new_score,
                "delta": new_score - base_score,
                "description": "Improve all language scores to CLB 10"
            }

    # French
    if not p.get("french_clb_scores"):
        sim = {**p, "french_clb_scores": [7, 7, 7, 7]}
        new_score = calculate_crs(sim)["total"]
        if new_score > base_score:
            results["add_french_clb7"] = {
                "new_score": new_score,
                "delta": new_score - base_score,
                "description": "Add French CLB 7 in all abilities"
            }

    # Canadian work experience
    if p.get("canadian_work_years", 0) < 5:
        sim = {**p, "canadian_work_years": p.get("canadian_work_years", 0) + 1}
        new_score = calculate_crs(sim)["total"]
        if new_score > base_score:
            results["one_more_canadian_work_year"] = {
                "new_score": new_score,
                "delta": new_score - base_score,
                "description": f"1 additional year of Canadian work experience"
            }

    # Job offer
    if not p.get("job_offer"):
        sim = {**p, "job_offer": True}
        new_score = calculate_crs(sim)["total"]
        if new_score > base_score:
            results["job_offer"] = {
                "new_score": new_score,
                "delta": new_score - base_score,
                "description": "Obtain a valid job offer (NOC 0, A, or B)"
            }

    sorted_results = dict(sorted(results.items(), key=lambda x: x[1]["delta"], reverse=True))
    return {
        "current_score": base_score,
        "target_score": target_score,
        "improvements": sorted_results
    }


def run_estimate_ita_timeline(crs_score: int, stream: str) -> dict:
    draws = run_get_draw_history(stream, limit=20)

    if "error" in draws:
        return draws

    cutoffs = [d["cutoff"] for d in draws["draws"]]
    qualifying = [c for c in cutoffs if crs_score >= c]
    percentage = round(len(qualifying) / len(cutoffs) * 100, 1)

    # Estimate draw frequency
    dates = [d["date"] for d in draws["draws"]]
    if len(dates) >= 2:
        from datetime import datetime
        d1 = datetime.strptime(dates[0], "%Y-%m-%d")
        d2 = datetime.strptime(dates[-1], "%Y-%m-%d")
        avg_days_between = (d1 - d2).days / (len(dates) - 1)
    else:
        avg_days_between = 14

    if percentage == 100:
        outlook = "Very strong — you would have qualified in all recent draws"
        estimated_wait = f"{round(avg_days_between)} days (next draw)"
    elif percentage >= 75:
        outlook = "Strong — you would have qualified in most recent draws"
        estimated_wait = f"{round(avg_days_between * 2)} days (1-2 draws)"
    elif percentage >= 50:
        outlook = "Moderate — you would have qualified in about half of recent draws"
        estimated_wait = f"1-3 months"
    else:
        outlook = "Below recent cutoffs — score improvement recommended before expecting an ITA"
        estimated_wait = "Uncertain — depends on score improvement"

    return {
        "crs_score": crs_score,
        "stream": stream,
        "qualifying_percentage": percentage,
        "outlook": outlook,
        "estimated_wait": estimated_wait,
        "latest_cutoff": draws["latest_cutoff"],
        "average_cutoff": draws["average_cutoff"],
        "draws_analyzed": draws["total_draws"]
    }


#  TOOL DISPATCHER ─

def execute_tool(tool_name: str, tool_input: dict) -> str:
    print(f"📥 INPUT: {json.dumps(tool_input, indent=2)}")  # ADD THIS
    try:
        if tool_name == "calculate_crs":
            result = run_calculate_crs(tool_input["profile"])
        elif tool_name == "get_draw_history":
            result = run_get_draw_history(
                tool_input["stream"],
                tool_input.get("limit", 10)
            )
        elif tool_name == "compare_scenarios":
            result = run_compare_scenarios(
                tool_input["profile_a"],
                tool_input["profile_b"],
                tool_input["label_a"],
                tool_input["label_b"]
            )
        elif tool_name == "get_score_gaps":
            result = run_get_score_gaps(
                tool_input["profile"],
                tool_input.get("target_score")
            )
        elif tool_name == "estimate_ita_timeline":
            result = run_estimate_ita_timeline(
                tool_input["crs_score"],
                tool_input["stream"]
            )
        else:
            result = {"error": f"Unknown tool: {tool_name}"}
    except Exception as e:
        result = {"error": str(e)}

    return json.dumps(result)


#  MAIN CHAT FUNCTION ─

async def chat(messages: list[dict]) -> str:
    tool_calls_made = 0

    # Build dynamic system prompt with profile context
    system = SYSTEM_PROMPT

    if messages and messages[0]["role"] == "user":
        system += f"\n\n{messages[0]['content']}"
        # Send remaining messages only (skip the system context message)
        messages = messages[1:]

    while tool_calls_made <= MAX_TOOL_CALLS:
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=system,
            tools=TOOLS,
            messages=messages
        )

        # Claude wants to call a tool
        if response.stop_reason == "tool_use":
            # Add Claude's response to message history
            messages.append({
                "role": "assistant",
                "content": response.content
            })

            # Execute all requested tools
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    tool_calls_made += 1
                    result = execute_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })

            # Add tool results to message history
            messages.append({
                "role": "user",
                "content": tool_results
            })

        # Claude is done — return final answer
        elif response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text
            return "I was unable to generate a response."

        else:
            return "Unexpected response from AI."

    return "I reached the maximum number of tool calls. Please try asking in a simpler way."


#  STREAMING (optional — for later) 

async def chat_stream(messages: list[dict]):
    reply = await chat(messages)
    import json as _json
    for token in reply.split(" "):
        yield f"data: {_json.dumps({'token': token + ' '})}\n\n"
    yield "data: [DONE]\n\n"