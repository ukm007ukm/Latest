import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import requests
from bs4 import BeautifulSoup
from fpdf import FPDF
from datetime import datetime

# Configuration
sender_email = "007aiyt@gmail.com"
receiver_email = "7haveli7@gmail.com"
app_password = "ckrfoxotcyxqzgrq"
smtp_server = "smtp.gmail.com"
smtp_port = 587

SOURCES = {
    "PIB Press Releases": "https://pib.gov.in/PressReleasePage.aspx",
    "InsightsIAS": "https://www.insightsonindia.com/current-affairs/",
    "Jagran Josh - UPSC": "https://www.jagranjosh.com/upsc"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def scrape_current_affairs():
    print("[*] Scraping UPSC Current Affairs...")
    messages = []

    for title, url in SOURCES.items():
        try:
            res = requests.get(url, headers=HEADERS, timeout=15)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, "html.parser")

            links = soup.find_all("a", href=True)
            relevant = []

            for link in links:
                text = link.get_text(strip=True).lower()
                if any(k in text for k in ["upsc", "current affairs", "civil services", "ias", "exam"]):
                    relevant.append(link.get_text(strip=True))

            if relevant:
                messages.append(f"🔎 {title}:\n" + "\n".join(relevant[:10]))
            else:
                messages.append(f"🔎 {title}:\nNo relevant updates right now.")

        except Exception as e:
            messages.append(f"🔎 {title}:\nError: {e}")

    return "\n\n".join(messages)

def generate_pdf(content, filename="upsc_digest.pdf"):
    print("[*] Generating PDF...")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in content.split("\n"):
        pdf.cell(200, 10, txt=line.encode("latin-1", "replace").decode("latin-1"), ln=True)
    pdf.output(filename)

def send_email(subject, body, attachment_path):
    print("[*] Sending Email...")
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    with open(attachment_path, "rb") as f:
        part = MIMEApplication(f.read(), Name="upsc_digest.pdf")
        part["Content-Disposition"] = 'attachment; filename="upsc_digest.pdf"'
        msg.attach(part)

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, app_password)
            server.send_message(msg)
        print("[✓] Email sent successfully.")
    except smtplib.SMTPAuthenticationError as e:
        print("[!] Authentication Error:", e)
    except Exception as e:
        print("[!] Failed to send:", e)

if __name__ == "__main__":
    print("[*] Running at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    message = scrape_current_affairs()
    generate_pdf(message)
    send_email("UPSC Current Affairs Digest", message, "upsc_digest.pdf")
