import subprocess
import json

def llama_query(prompt: str, model="llama3.1") -> str:
    """
    Run a query against local Ollama model and return the raw text.
    """
    result = subprocess.run(
        ["ollama", "run", model],
        input=prompt.encode("utf-8"),
        capture_output=True
    )
    return result.stdout.decode("utf-8").strip()


def pick_top_headlines(sector: str, headlines: list[str]) -> list[str]:
    """
    Ask LLaMA to pick top 3 most important headlines.
    """
    prompt = f"""
You are an editor. Here are the latest headlines in the {sector} sector:

{chr(10).join(f"- {h}" for h in headlines)}

Pick the 3 most important headlines that any person should definitely know. Return ONLY a JSON list like this:
["headline1", "headline2", "headline3"]
"""
    response = llama_query(prompt)
    try:
        return json.loads(response)
    except Exception:
        # fallback: just return first 3
        return headlines[:3]
