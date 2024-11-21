import os
from dotenv import load_dotenv  # Für das Laden der .env-Datei
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options  # Für den Headless-Modus
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time

# .env-Datei laden
load_dotenv()

# Einstellungen aus der .env-Datei lesen
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH")
BASE_URL = os.getenv("BASE_URL")
PASSWORD = os.getenv("PASSWORD")

# WebDriver-Setup mit Headless-Modus
chrome_options = Options()
chrome_options.add_argument("--headless")  # Aktiviert den Headless-Modus
chrome_options.add_argument("--disable-gpu")  # Nützlich für Kompatibilität
chrome_options.add_argument("--window-size=1920,1080")  # Setzt eine virtuelle Fenstergröße
chrome_options.add_argument("--no-sandbox")  # Optional für Linux
chrome_options.add_argument("--disable-dev-shm-usage")  # Optional für Linux

service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=chrome_options)

def login_to_mailman():
    try:
        driver.get(BASE_URL)

        # Warte, bis das Login-Formular geladen ist
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "adminpw"))
        )

        # Login-Daten eingeben
        password_field = driver.find_element(By.NAME, "adminpw")
        password_field.send_keys(PASSWORD)

        # Formular absenden
        password_field.send_keys(Keys.RETURN)

        # Warte, bis der Login abgeschlossen ist
        WebDriverWait(driver, 10).until(
            EC.url_contains("admin")
        )
        print("Login erfolgreich!")
    except Exception as e:
        print(f"Login fehlgeschlagen: {e}")
        driver.quit()

def scrape_emails(members_base_url):
    ALPHABET = "abcdefghijklmnopqrstuvwxyz"
    emails = []

    try:
        for letter in ALPHABET:
            url = f"{members_base_url}?letter={letter}"
            driver.get(url)

            # Warte auf das Laden der Seite
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//table"))
            )

            # Extrahiere die E-Mail-Adressen aus der Tabelle
            rows = driver.find_elements(By.XPATH, "//table//tr")
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) > 1:  # Stelle sicher, dass es sich um eine valide Zeile handelt
                    email = cells[1].text.strip()  # Annahme: E-Mail-Adresse ist in der zweiten Spalte
                    if "@" in email:
                        emails.append(email)

            print(f"Seite {letter} verarbeitet, {len(emails)} E-Mails gefunden.")
            time.sleep(2)  # Kleine Pause, um Serverlast zu vermeiden
    except Exception as e:
        print(f"Fehler beim Abrufen der E-Mails: {e}")

    # Entferne Duplikate
    unique_emails = list(set(emails))
    print(f"Duplikate entfernt: {len(emails) - len(unique_emails)} Duplikate gefunden.")
    return unique_emails

def save_to_csv(emails):
    # Interaktive Eingabe des Dateinamens
    output_file = input("Bitte den Dateinamen für die CSV-Ausgabe eingeben (z. B. mailman_emails.csv): ").strip()

    try:
        with open(output_file, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Email"])  # Header
            for email in sorted(emails):  # Optional: Sortiere die E-Mails alphabetisch
                writer.writerow([email])
        print(f"E-Mails erfolgreich in {output_file} gespeichert!")
    except Exception as e:
        print(f"Fehler beim Speichern der Datei: {e}")

def main():
    login_to_mailman()

    # Generiere members_base_url aus BASE_URL
    members_base_url = f"{BASE_URL}/members"

    emails = scrape_emails(members_base_url)
    save_to_csv(emails)

    driver.quit()

if __name__ == "__main__":
    main()