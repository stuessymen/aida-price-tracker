import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import os

# 🔧 Konfiguration
URL = "https://aida.de/kreuzfahrt/angebote/aida-vario"
CSS_SELECTOR = ".price__amount"  # 🔍 Mit Browser-DevTools prüfen!
EMAIL_FROM = os.getenv("GMAIL_USER")  # Deine Gmail (über GitHub Secrets)
EMAIL_TO = "stuessymen@gmail.com"  # 👈 Deine Empfänger-E-Mail
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")  # Google App-Passwort

def get_price():
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    return soup.select_one(CSS_SELECTOR).text.strip()

def send_email(old_price, new_price):
    # Umwandlung in Zahlen (entfernt € und Leerzeichen)
    old_num = float(old_price.replace("€", "").replace(",", ".").strip())
    new_num = float(new_price.replace("€", "").replace(",", ".").strip())
    
    # Trendberechnung
    if new_num < old_num:
        trend = f"gesunken 🎉 (Ersparnis: {old_num - new_num:.2f} €)"
    else:
        trend = f"gestiegen 📈 (Mehrkosten: {new_num - old_num:.2f} €)"
    
    # E-Mail-Inhalt
    msg = MIMEText(
        f"🚢 AIDA Vario-Preis-Update:\n\n"
        f"• Neuer Preis: {new_price}\n"
        f"• Trend: {trend}\n\n"
        f"🔗 Link: {URL}"
    )
    msg["Subject"] = f"🔔 AIDA-Preis {trend.split()[0]}!"
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO

    # E-Mail senden
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_FROM, GMAIL_PASSWORD)
        server.send_message(msg)

# 🚀 Hauptlogik
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
    print("Fehler:", # 👇 TEST: Manuellen Preisalarm auslösen (kommentiere danach aus!)
print("Sende Test-E-Mail...")
send_email("999 €", get_price())  # Ersetze "999 €" durch einen Dummy-Preis 
    