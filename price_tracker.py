import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import os

# 🔧 Konfiguration
URL = "https://aida.de/kreuzfahrt/angebote/aida-vario"
CSS_SELECTOR = ".price__amount"  # 🔍 Mit Browser-DevTools prüfen!
EMAIL_FROM = os.getenv("GMAIL_USER")  # Aus GitHub Secrets
EMAIL_TO = "stuessymen@gmail.com"  # Deine Empfänger-Mail
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")  # GitHub Secret

def get_price():
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(URL, headers=headers)
        response.raise_for_status()  # Prüft auf HTTP-Fehler
        soup = BeautifulSoup(response.text, "html.parser")
        price_element = soup.select_one(CSS_SELECTOR)
        if not price_element:
            raise ValueError("CSS-Selektor nicht gefunden!")
        return price_element.text.strip()
    except Exception as e:
        print(f"Fehler beim Preis-Check: {e}")
        return None

def send_email(old_price, new_price):
    try:
        # Umwandlung in Zahlen (falls € oder Kommas stören)
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
            f"• Vorher: {old_price}\n"
            f"• Jetzt: {new_price}\n"
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
        print("✅ E-Mail gesendet!")
    except Exception as e:
        print(f"Fehler beim E-Mail-Versand: {e}")

# 🚀 Hauptlogik
try:
    current_price = get_price()
    if current_price is None:
        raise ValueError("Preis konnte nicht abgerufen werden!")

    if os.path.exists("last_price.txt"):
        with open("last_price.txt", "r") as f:
            last_price = f.read().strip()
        if current_price != last_price:
            send_email(last_price, current_price)
    else:
        print("Erster Lauf – keine Preisänderung vorhanden.")

    with open("last_price.txt", "w") as f:
        f.write(current_price)
except Exception as e:
    print(f"Kritischer Fehler: {e}")