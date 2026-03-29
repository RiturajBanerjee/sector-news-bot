import os
import sqlite3
import json
from openai import OpenAI
import ollama
from dotenv import load_dotenv
from llm_local import pick_top_headlines
from newspaper import Article

load_dotenv()
#client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DB_NAME = "news.db"


# --- Fetch news items that need summarization ---
def get_unsummarized_news():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, title, link, sector FROM news WHERE summary IS NULL OR summary=''")
    rows = c.fetchall()
    conn.close()
    return rows


# # --- Call OpenAI Responses API to summarize + score ---
# def summarize_text(article_text: str) -> str:
#     prompt = f"""
# You are a journalist. Summarize the following article into:
# 1) A 1-sentence headline summary (<= 25 words).
# 2) 2-sentence detailed summary (<= 40 words).
# 3) 3 key bullets (one short fact each).
# 4) One-line "Why it matters" (<= 20 words).

# Return JSON strictly in this format:
# {{
#   "headline": "...",
#   "summary": "...",
#   "bullets": ["...", "...", "..."],
#   "impact": "...",
# }}

# Article:
# <<<{article_text}>>>
# """

#     response = client.responses.create(
#         model="gpt-5-nano", 
#         input=prompt,
#     )
#     print("-----")
#     print(prompt)
#     print("-----")
#     if hasattr(response, "output_text") and response.output_text:
#         return response.output_text.strip()

#     if response.output and len(response.output) > 0 and response.output[0].content:
#         output_text = ""
#         for content in response.output[0].content:
#             if getattr(content, "type", None) == "output_text":
#                 output_text += content.text
#         return output_text.strip()
#     return "{}"
def summarize_text(article_text: str) -> str:
    prompt = f"""
You are a journalist. Summarize the following article into:
1) A 1-sentence headline summary (<= 25 words).
2) 2-sentence detailed summary (<= 40 words).
3) 3 key bullets (one short fact each).
4) One-line "Why it matters" (<= 20 words).

Return JSON and JSON only strictly in this format:
{{
  "headline": "...",
  "summary": "...",
  "bullets": ["...", "...", "..."],
  "impact": "...",
}}

Article:
<<<{article_text}>>>
"""

    # Call Ollama
    response = ollama.chat(
        model="llama3.1",  # change to your local model name, e.g. "mistral", "llama2", etc.
        messages=[{"role": "user", "content": prompt}]
    )

    # Extract text
    output_text = response["message"]["content"].strip()

    # Ensure valid JSON
    try:
        json.loads(output_text)
    except Exception:
        print("Model did not return valid JSON, wrapping in {}")
        return "{}"

    return output_text

# --- Save back into DB ---
def update_summary(news_id, summary_json):
    try:
        parsed = json.loads(summary_json)
        summary = json.dumps(parsed, ensure_ascii=False)
    except Exception:
        summary = summary_json

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE news SET summary=? WHERE id=?", (summary, news_id))
    conn.commit()
    conn.close()

def fetch_article_content(url: str, fallback_title: str) -> str:
    try:
        article = Article(url)
        article.download()
        article.parse()
        text = article.text.strip()
        if not text:
            print(f"Failed to fetch text, returning title :{fallback_title}")
            return fallback_title  # fallback to just title
        return text
    except Exception as e:
        print(f"⚠️ Failed to fetch article content from {url}: {e}")
        return fallback_title
    
# --- For manual testing without DB ---
def test_single_article():
    sample_article = """
    Apple has announced the launch of the iPhone 16 with new AI-powered features,
    including on-device generative AI, a redesigned camera system, and longer battery life.
    Analysts say this could reshape competition with Samsung and Google in the premium segment.
    """
    summary_json = summarize_text(sample_article)
    print("\n=== Test Output ===")
    print(summary_json)

def perform_summarization():
    print(" Fetching unsummarized news...")
    rows = get_unsummarized_news()
    print(f" Retrieved {len(rows)} rows")
    sectors ={}
    for nid, title, link, sector in rows:
        sectors.setdefault(sector, []).append((nid, title, link))
    print(f" Grouped into {len(sectors)} sectors")
    for sector, items in sectors.items():
        print(f"\n=== Processing sector: {sector.upper()} ===")
        headlines = [title for (_, title, _) in items]
        print(f" Total headlines: {len(headlines)}")
        top3 = pick_top_headlines(sector, headlines)
        print(f"Picked top 3 headlines :\n{top3}")
        for (nid, title, link) in items:
            if title in top3:
                print(f"Summarizing: {title}")
                article_text = fetch_article_content(link, title)
                summary_json = summarize_text(article_text)
                update_summary(nid, summary_json)
                print(f"✅ {sector.upper()} - summarized {title}")

# --- Main entry ---
if __name__ == "__main__":
    # 🔹 Uncomment to test DB flow
    perform_summarization()

    # 🔹 Test mode (no DB, just a sample article)
    #test_single_article()
