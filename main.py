import datetime
import csv
import concurrent.futures

# from link_extractor import get_all_links, concat_csv_files
from caracteristicas import procesar_enlace, Oferta

# get_all_links()
# concat_csv_files()

lista_ofertas = []

offers_csv_filename = f"./ofertas/ofertas-{datetime.datetime.now().timestamp()}.csv"
offers_csv_file = open(offers_csv_filename, 'w', encoding='utf-8')
offers_csv_writer = csv.writer(offers_csv_file)
offers_csv_writer.writerow(Oferta._fields)

def scrape_link(prefix, link):
    oferta = procesar_enlace(prefix=prefix, link=link)
    offers_csv_writer.writerow(oferta)

with open('./output/merged_links.csv', newline='') as merged_links_csv_file:
    mapped_links_to_scrape = list(csv.reader(merged_links_csv_file))[1:]
    links_to_scrape = [link[1] for link in mapped_links_to_scrape]

total_links = len(links_to_scrape)
max_workers = 5

with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
    futures = [
        executor.submit(scrape_link, f"{index + 1}/{total_links}", link_to_scrape)
        for index, link_to_scrape in enumerate(links_to_scrape)
    ]

offers_csv_file.close()
merged_links_csv_file.close()

print(f"Datos guardados en {offers_csv_filename}")
