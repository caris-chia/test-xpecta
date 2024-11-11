import glob
import datetime
import concurrent.futures
import csv
import pandas as pd

from collections import namedtuple
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

Enlace = namedtuple("Enlace", [
    "link",
    "created_at",
    "scraped_at"
])

chrome_options = Options()
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--disable-popup-blocking")
chrome_options.add_experimental_option(
    "prefs", {
        "profile.managed_default_content_settings.images": 2,
    }
)

def get_links_from_page(url, page_number):
    print(f"Obteniendo enlaces de la pagina #{page_number} {url}")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    lista_enlaces = []

    try:
        wait = WebDriverWait(driver, timeout=10)
        wait.until(
            EC.visibility_of_element_located((By.CLASS_NAME, "listingsWrapper"))
        )

        anchors = driver.find_elements(By.XPATH, '//*[@class="listingsWrapper"]/div/a')

        for anchor in anchors:
            enlace = anchor.get_attribute("href")
            lista_enlaces.append(Enlace(
                link=enlace,
                created_at=datetime.datetime.now(),
                scraped_at=None
            ))

        csv_filename = f"./links_per_thread/links_page_{page_number}.csv"
        csv_file = open(csv_filename, 'w', newline='', encoding='utf-8')

        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(Enlace._fields)
        csv_writer.writerows(lista_enlaces)
        csv_file.close()
        print(f"Pagina {page_number} - guardados {len(lista_enlaces)} enlaces en archivo {csv_filename}")
    finally:
        driver.quit()

def get_all_links():
    start_page_number = 11
    total_results = 42024
    results_per_page = 21
    total_pages = total_results // results_per_page

    print(f"Total de resultados: {total_results}")
    print(f"Resultados por pagina: {results_per_page}")
    print(f"Total de paginas: {total_pages}")

    max_workers = 5
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        start_page = "https://www.fincaraiz.com.co/venta/apartamentos/bogota/bogota-dc"

        for page in range(start_page_number, total_pages):
            if page == 1:
                url = start_page
            else:
                url = f"{start_page}/pagina{page}"

            executor.submit(get_links_from_page, url, page)

def concat_csv_files(file_path):
    csv_files = glob.glob(file_path + '/*.csv')
    df_append = pd.DataFrame()

    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        df_append = pd.concat([df_append, df], ignore_index=True)

    return df_append
