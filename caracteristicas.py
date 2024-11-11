import json


from selenium import webdriver #Para manejar el navegador
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup
from collections import namedtuple


Oferta = namedtuple("Oferta", [
    "price",
    "address",
    "coordinates_lat",
    "coordinates_lng",
    "main_location",
    "link",
    "social_stratum",
    "property_type",
    "state",
    "bathrooms",
    "constructed_area",
    "private_area",
    "age",
    "rooms",
    "parking_spaces",
    "administration",
    "floor_number",
    "remodeled"
])

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--disable-popup-blocking")

def procesar_enlace(prefix, link):
    print(f"Procesando enlace {prefix} - {link}")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(link)

    try:
        property_detail_container = driver.find_element(By.CLASS_NAME, 'property-detail')

        wait = WebDriverWait(driver, timeout=2)
        wait.until(lambda d : property_detail_container.is_displayed())

        html_content = driver.page_source
        soup = BeautifulSoup(html_content, "html.parser")

        data_html = soup.find("script", type="application/ld+json") #Busqueda por Tag HTML
        data_text = data_html.get_text()
        data_json = json.loads(data_text)

        price = data_json["priceSpecification"]["price"]
        # print(f"price: {price}")

        address = data_json["object"]["address"]
        # print(f"address: {address}")

        coordinates_lat = data_json["object"]["geo"]["latitude"]
        # print(f"coordinates_lat: {coordinates_lat}")

        coordinates_lng = data_json["object"]["geo"]["longitude"]
        # print(f"coordinates_lng: {coordinates_lng}")

        main_location_html = soup.select_one('div[class^="ant-row location-header"]>.ant-col>.body-regular.medium') #Selecciona el primero del selector de CSS
        main_location = main_location_html.get_text() #Obtiene el texto
        # print(f"main_location: {main_location}")

        technical_sheet_rows = soup.select('div[class^="jsx-952467510 technical-sheet"]>.ant-row') # Selecciona todos los elementos que tenga la clase ant-row

        for technical_sheet_row in technical_sheet_rows: #Evaluar la lista de elementos que contiene technical_seet_rows
            row_columns = technical_sheet_row.select('div[class^="ant-col"]')

            row_col_title_html = row_columns[0].select_one('div[class^="ant-space-item"] span.ant-typography:not(.small)') #Tenian la misma estructura por ello se extrae el titulo y el valor
            row_col_title = row_col_title_html.get_text()

            row_col_value_html = row_columns[2].select_one('div[class^="ant-typography"] strong')
            row_col_value = ""

            if row_col_value_html != None:
                row_col_value = row_col_value_html.get_text()

            if row_col_title == "Estrato":
                social_stratum = row_col_value

            if row_col_title == "Tipo de Inmueble":
                property_type = row_col_value

            if row_col_title == "Estado":
                state = row_col_value

            if row_col_title == "Baños":
                bathrooms = row_col_value

            if row_col_title == "Área Construida":
                constructed_area = row_col_value

            if row_col_title == "Área Privada":
                private_area = row_col_value

            if row_col_title == "Antigüedad":
                age = row_col_value

            if row_col_title == "Habitaciones":
                rooms = row_col_value

            if row_col_title == "Parqueaderos":
                parking_spaces = row_col_value

            if row_col_title == "Administración":
                administration = row_col_value

            if row_col_title == "Piso N°":
                floor_number = row_col_value

            if row_col_title == "Remodelado":
                remodeled = row_col_value

        return Oferta(
            price=price,
            address=address,
            coordinates_lat=coordinates_lat,
            coordinates_lng=coordinates_lng,
            main_location=main_location,
            link=link,
            social_stratum=social_stratum,
            property_type=property_type,
            state=state,
            bathrooms=bathrooms,
            constructed_area=constructed_area,
            private_area=private_area,
            age=age,
            rooms=rooms,
            parking_spaces=parking_spaces,
            administration=administration,
            floor_number=floor_number,
            remodeled=remodeled
        )

    except Exception as e:
        print(f"Error en el enlace {link}: {str(e)}")

    driver.quit()