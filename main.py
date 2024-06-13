import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import datetime
from selenium.webdriver.chrome.service import Service
import math
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import pandas
from Reader import Reader
from selenium.common.exceptions import TimeoutException

def getdata():
    rd = Reader()
    rd.openExplorer()
    data = pandas.read_csv(filepath_or_buffer=rd.path, sep  = ";")
    return data.iloc[:, 0]

def popups(driver):
    try:
        WebDriverWait(driver, 0.5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="onetrust-accept-btn-handler"]'))).click()
        WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PromoteSignUpPopUp"]/div[2]/i'))).click()
    except Exception:
        pass

def tableAvailable(driver):
    try:
        WebDriverWait(driver, 0.5).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="eventTabDiv_history_0"]')))
        return True
    except Exception:
        print("Keine Tabelle vorhanden bei: " + str(driver.current_url))
        return False

daten = getdata()

driver = webdriver.Chrome()

def load_page_with_timeout(url, timeout, retries):
    attempt = 0
    while attempt < retries:
        try:
            # print(f"Versuch {attempt + 1}, lade Seite: {url}")
            # Setze die maximale Ladezeit für die Seite
            driver.set_page_load_timeout(timeout)
            driver.get(url)
            # Wenn die Seite erfolgreich geladen wird, beenden wir die Schleife
            return
        except TimeoutException:
            # print(f"Seite hat nach {timeout} Sekunden nicht geladen. Versuch {attempt + 1} von {retries}.")
            attempt += 1
            if attempt < retries:
                # print("Seite neu laden...")
                driver.refresh()
                time.sleep(1)  # Warte ein wenig bevor du es erneut versuchst
            else:
                # print("Seite konnte nicht geladen werden. Alle Versuche fehlgeschlagen.")
                raise

final_data = []

for link in daten:
    # driver.get(link)
    try:
        load_page_with_timeout(link, 6, 2)
    except Exception:
        continue
    popups(driver)
    if tableAvailable(driver):
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        tbody = soup.find("tbody")
        for tr in tbody.find_all("tr"):
            tds = tr.find_all("td")[:-1]
            data = [td.get_text(strip=True) for td in tds]
            data.append(link)
            final_data.append(data)
        # print("Tabelle vorhanden")
    else:
        continue

columns = ['Geschichte', 'Zeit', 'Aktuell', 'Prognose', 'Vorherig', 'Link']

df = pandas.DataFrame(final_data, columns=columns)

df2 = pandas.DataFrame(final_data)

filename = "investing_" + datetime.datetime.strftime(datetime.datetime.now(), "%d.%m.%y_%H%M") + ".csv"

filename2 = "investing_" + datetime.datetime.strftime(datetime.datetime.now(), "%d.%m.%y_%H%M") + "_" + str(2) + ".csv"

try:
    # df.to_csv('/Users/justinwild/Downloads/' + filename, sep = ";", index = False, encoding = 'utf-8')
    df.to_csv('//Master/F/User/Microsoft Excel/Privat/Börse/Investing/' + filename, sep = ";", index = False, encoding = 'utf-8')

except Exception:
    print("Spalten passen nicht, daher ohne Bezeichnung ausgeworfen!")
    # df2.to_csv('/Users/justinwild/Downloads/' + filename2, sep = ";", index = False, encoding = 'utf-8')
    df2.to_csv('//Master/F/User/Microsoft Excel/Privat/Börse/Investing/' + filename2, sep=";", index=False, encoding='utf-8')