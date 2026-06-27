import os
import json
import google.generativeai as genai
from google.generativeai import GenerativeModel
from dotenv import load_dotenv

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY"),
    client_options={"api_endpoint": "generativelanguage.googleapis.com"}
)

model = GenerativeModel("gemini-2.0-flash")


SYSTEM_PROMPT = """
You are an expert at analyzing LinkedIn posts for corporate jargon,
buzzwords, and performative language. You give honest, slightly witty
but fair assessments.

You will be given a LinkedIn caption. Analyze it and return a JSON object
with exactly these fields:

{
  "cringe_score": <integer 0-100>,
  "verdict": "<one sentence summary of the post's tone>",
  "reasons": ["<reason 1>", "<reason 2>", "<reason 3>"],
  "rewrite": "<a cleaner, more human version of the same post>"
}

Scoring guide:
- 0-20: Genuine and human, minimal jargon
- 21-40: Mostly fine, a few buzzwords
- 41-60: Noticeable corporate tone
- 61-80: Heavy jargon, performative
- 81-100: Peak LinkedIn cringe

Return ONLY the raw JSON object. No markdown, no backticks, no explanation.
"""


def analyze_with_gemini(post_text: str) -> dict:
    prompt = f"{SYSTEM_PROMPT}\n\nLinkedIn post:\n{post_text}"

    try:
        response = model.generate_content(prompt)
        raw = response.text.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        result = json.loads(raw)

        required_keys = {"cringe_score", "verdict", "reasons", "rewrite"}
        if not required_keys.issubset(result.keys()):
            raise ValueError("Missing keys in Gemini response")

        return {"success": True, "data": result}

    except json.JSONDecodeError:
        return {"success": False, "error": "Gemini returned invalid JSON. Try again."}
    except Exception as e:
        return {"success": False, "error": str(e)}


def analyze_all_posts(posts: list[dict]) -> list[dict]:
    enriched = []
    for post in posts:
        gemini_result = analyze_with_gemini(post["text"])
        post["gemini"] = gemini_result
        enriched.append(post)
    return enriched
