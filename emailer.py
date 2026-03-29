import os, smtplib, sqlite3, json
from email.mime.text import MIMEText
from dotenv import load_dotenv
import json
from collections import defaultdict

load_dotenv()
DB_NAME = "news.db"

def fetch_latest_news(limit=30):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT sector, summary, link FROM news WHERE summary IS NOT NULL AND summary !='' ORDER BY created_at DESC LIMIT ?", 
              (limit,))
    rows = c.fetchall()
    conn.close()
    return rows

def build_email_body(rows):
    # Group news by sector
    grouped = defaultdict(list)
    for sector, summary_json, url in rows:
        grouped[sector].append((summary_json, url))

    body = ""

    for sector, items in grouped.items():
        sector_block = f"""
        <div style="border:1px solid #e0e0e0; border-radius:8px; padding:16px; margin-bottom:20px; background:#fafafa;">
            <h2 style="color:#2C3E50; margin:0 0 15px 0; border-bottom:2px solid #eee; padding-bottom:6px;">
                📌 {sector.title()}
            </h2>
        """
        for summary_json, url in items:
            try:
                parsed = json.loads(summary_json)
                sector_block += f"""
                <div style="margin-bottom:18px; padding-bottom:12px; border-bottom:1px dashed #ddd;">
                    <h3 style="color:#8E44AD; margin:0;">📰 {parsed['headline']}</h3>
                    <p style="margin:6px 0 10px 0; font-size:14px; line-height:1.5; color:#333;">
                        {parsed['summary']}
                    </p>
                    <ul style="margin:0 0 10px 20px; color:#555;">
                        {''.join(f"<li>{bullet}</li>" for bullet in parsed['bullets'])}
                    </ul>
                    <p style="margin:6px 0; font-size:14px;">
                        💡 <i>Why it matters:</i> {parsed['impact']}
                    </p>
                    {"<p style='margin:8px 0;'><a href='"+url+"' style='color:#2980B9; text-decoration:none; font-weight:bold;'>🔗 Read more →</a></p>" if url else ""}
                </div>
                """
            except Exception:
                sector_block += f"<p>{summary_json}</p>"

        sector_block += "</div>"
        body += sector_block

    if not body.strip():
        body = "<p>No high-importance news today!</p>"

    return f"""
    <html>
      <body style="font-family:Arial, sans-serif; background:#f4f4f4; padding:20px; color:#333;">
        <div style="max-width:600px; margin:auto; background:#fff; padding:20px; border-radius:10px; box-shadow:0 2px 6px rgba(0,0,0,0.1);">
          <h1 style="text-align:center; color:#2C3E50;">📢 Daily Sector News Digest</h1>
          {body}
          <p style="font-size:12px; color:#888; text-align:center; margin-top:30px;">
            You are receiving this email because you subscribed to Daily News Digest.<br>
            © {2025} Crisp News Bot
          </p>
        </div>
      </body>
    </html>
    """
def send_email(rows=None):
    # If no rows are passed, fetch from DB
    if rows is None:
        rows = fetch_latest_news()

    body = build_email_body(rows)

    msg = MIMEText(body,"html")
    msg["Subject"] = "Daily Sector News Digest"
    msg["From"] = os.getenv("EMAIL_USER")
    msg["To"] = os.getenv("EMAIL_TO_USERS")

    with smtplib.SMTP(os.getenv("EMAIL_HOST"), int(os.getenv("EMAIL_PORT"))) as server:
        server.starttls()
        server.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASS"))
        server.sendmail(msg["From"], [msg["To"]], msg.as_string())
    print("✅ Email sent!")

# ------------------ TESTING HOOK ------------------
def test_emailer():
    dummy_rows = [
        ("tech", json.dumps({
            "headline": "AI Startups Secure Record Funding",
            "summary": "AI firms raised $5B in Q2, led by Sequoia and Accel.",
            "bullets": ["Funding hit $5B", "Focus on GenAI tools", "Investors: Sequoia, Accel"],
            "impact": "Signals strong investor confidence in AI growth"
        }), "https://example.com/ai-funding"),
        ("finance", json.dumps({
            "headline": "Markets Rally Amid Rate Cut Hopes",
            "summary": "Global markets surged after central banks hinted at possible rate cuts.",
            "bullets": ["Stocks up 3%", "Bonds stabilize", "Investors optimistic"],
            "impact": "Improved sentiment could fuel more capital inflows"
        }), "https://example.com/markets-rally")
    ]
    send_email(dummy_rows)


if __name__ == "__main__":
    # Normal run → pulls from DB
    send_email()

    # Test run → uses dummy data (no DB needed)
    #test_emailer()
