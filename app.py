import yfinance as yf
import requests, feedparser, smtplib, os
from fpdf import FPDF
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime

# 📩 Email config — replace with yours
FROM_EMAIL = "007aiyt@gmail.com"
EMAIL_PASSWORD = "ckrfoxotcyxqzgrq"
TO_EMAIL = "7haveli7@gmail.com"

def fetch_news():
    feed = feedparser.parse("https://news.google.com/rss/search?q=rpower")
    return "\n".join([f"- {e.title}\n  {e.link}" for e in feed.entries[:3]]) or "No recent news."

def fetch_financials():
    ticker = yf.Ticker("RPOWER.NS")
    info = ticker.info
    fin = {
        "P/E Ratio": info.get("trailingPE", "N/A"),
        "Market Cap": f"{info.get('marketCap', 'N/A'):,}" if info.get("marketCap") else "N/A",
        "Profit Margin (%)": info.get("profitMargins", "N/A"),
        "Operating Margin (%)": info.get("operatingMargins", "N/A"),
        "Quarterly PAT (₹ Crore)": (
            f"{ticker.quarterly_financials.loc['Net Income', :].iloc[0]/1e7:.2f}"
            if hasattr(ticker, "quarterly_financials") and "Net Income" in ticker.quarterly_financials.index
            else "N/A"
        )
    }
    return fin

def fetch_shareholding():
    ticker = yf.Ticker("RPOWER.NS")
    inst = ticker.institutional_holders
    if inst is None or inst.empty:
        return {"Institutional Holders": "N/A"}
    top = inst.sort_values('Shares', ascending=False).head(3)
    return {row['Holder']: f"{row['Shares']:,}" for _, row in top.iterrows()}

def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in text.split("\n"):
        pdf.multi_cell(0, 8, line.encode("latin-1", "ignore").decode("latin-1"))
    fname = f"RPower_Report_{datetime.now():%Y%m%d}.pdf"
    pdf.output(fname)
    return fname

def send_email(subject, body, attachment):
    msg = MIMEMultipart()
    msg["From"], msg["To"], msg["Subject"] = FROM_EMAIL, TO_EMAIL, subject
    msg.attach(MIMEText(body, "plain"))
    with open(attachment, "rb") as f:
        part = MIMEApplication(f.read(), _subtype="pdf")
        part.add_header("Content-Disposition", "attachment", filename=os.path.basename(attachment))
        msg.attach(part)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(FROM_EMAIL, EMAIL_PASSWORD)
        s.send_message(msg)

if __name__ == "__main__":
    news = fetch_news()
    fin = fetch_financials()
    holders = fetch_shareholding()

    content = (
        f"🗞️ RPower Daily Report — {datetime.now():%Y-%m-%d}\n\n"
        f"**News:**\n{news}\n\n**Financial Metrics:**\n"
        + "\n".join(f"{k}: {v}" for k, v in fin.items()) + "\n\n**Shareholding:**\n"
        + "\n".join(f"{k}: {v}" for k, v in holders.items())
    )

    pdf = create_pdf(content)
    send_email("📈 RPower Daily Financial Update", content, pdf)
    print("✅ Sent the daily report.")
