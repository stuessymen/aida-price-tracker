import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import os

URL = "https://aida.de/kreuzfahrt/angebote/aida-vario"
CSS_SELECTOR = ".price__amount"  # 🔍 Anpassen falls nötig!
EMAIL_FROM = os.getenv("GMAIL_USER")  # Deine Gmail (über Secrets gesetzt)
EMAIL_TO = "stuessymen@gmail.com"  # 👈 Deine E-Mail
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")  # App-Passwort

def get_price():
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    return soup.select_one(CSS_SELECTOR).text.strip()

def send_email(old_price, new_price):
    msg = MIMEText(f"🚢 AIDA-Preis geändert!\nVorher: {old_price}\nJetzt: {new_price}\n\nLink: {URL}")
    msg["Subject"] = "🔔 AIDA Preisalarm!"
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_FROM, GMAIL_PASSWORD)
        server.send_message(msg)

try:
    current_price = get_price()
    if os.path.exists("last_price.txt"):
        with open("last_price.txt", "r") as f:
            last_price = f.read().strip()
        if current_price != last_price:
            send_email(last_price, current_price)
    with open("last_price.txt", "w") as f:
        f.write(current_price)
except Exception as e:
    print("Fehler:", e)