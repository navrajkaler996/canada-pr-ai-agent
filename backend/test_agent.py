"""
Test script for PRCompass agentic AI agent.
Run this from your backend directory:
    python test_agent.py
"""

import asyncio
import json
from ai_agent import chat

# ─── SAMPLE PROFILE ───────────────────────────────────────────────────────────
# This simulates what your frontend should send after CRS calculation

SAMPLE_PROFILE = {
    "has_spouse": False,
    "age": 28,
    "education": "bachelors",
    "clb_speaking": 9,
    "clb_listening": 9,
    "clb_reading": 9,
    "clb_writing": 9,
    "canadian_work_years": 0,
    "foreign_work_years": 3,
    "first_language": "english",
    "has_canadian_sibling": False,
    "french_clb_scores": [],
    "canadian_education_years": 2,
    "has_provincial_nomination": False,
    "has_certificate": False,
    "spouse_education": None,
    "spouse_clb_speaking": None,
    "spouse_clb_listening": None,
    "spouse_clb_reading": None,
    "spouse_clb_writing": None,
    "spouse_canadian_work_years": None,
    "canadian_noc": None,
    "trade_certificate": False,
    "second_language_test": "none",
    "foreign_noc": None,
    "job_offer": False
}

# ─── TEST QUESTIONS ───────────────────────────────────────────────────────────

TESTS = [
    {
        "name": "Test 1 — ITA Timeline",
        "question": "When should I expect an ITA? I am eligible for Canadian Experience Class."
    },
    {
        "name": "Test 2 — Score Improvement",
        "question": "How can I improve my CRS score?"
    },
    {
        "name": "Test 3 — Scenario Comparison",
        "question": "What if I improve my language scores to CLB 10? How much would that help?"
    }
]

# ─── RUN TESTS ────────────────────────────────────────────────────────────────

async def run_test(name: str, question: str):
    print(f"\n{'='*60}")
    print(f"{name}")
    print(f"{'='*60}")
    print(f"Question: {question}")
    print(f"{'─'*60}")

    # This is how your frontend should format the first message
    # Profile + CRS + question all in one context message
    messages = [
        {
            "role": "user",
            "content": f"""Here is my profile:
{json.dumps(SAMPLE_PROFILE, indent=2)}

Question: {question}"""
        }
    ]

    try:
        reply = await chat(messages)
        print(f"Claude: {reply}")
        print(f"\n✅ PASSED")
    except Exception as e:
        print(f"\n❌ FAILED: {e}")


async def main():
    print("PRCompass Agent Test")
    print("Running 3 tests...\n")

    for test in TESTS:
        await run_test(test["name"], test["question"])
        # Small delay between tests to avoid rate limiting
        await asyncio.sleep(2)

    print(f"\n{'='*60}")
    print("All tests complete.")


if __name__ == "__main__":
    asyncio.run(main())