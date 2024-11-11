# Instrucciones:
Los documentos fueron creados con los siguientes objetivos:

1. link_extractor.py -> extrae los links desde las listas, por cada página se crea un archivo csv en el directorio links_per_thread
2. main.py, caracteristicas.py -> lee los enlaces desde merged_links.csv y extrae la información de cada uno en un proceso separado, el resultante es el archivo ofertas-*.csv
3. csv_updater.py -> lee las ofertas que fueron creadas (ofertas-*.csv) y compara contra la lista de enlaces que tenía que procesar (merged_links_*.csv), para aquellos registros que fueron procesados y el enlace aparezca en ofertas-*.py se marcará con un timestamp en el campo scaped_at
3.1. links_not_scraped.py -> lee el archivo merged_links_*.csv actualizado en el proceso anterior y toma aquellos registros cuya columna scraped_at esta vacía, esto indica que el al enlace de este registro aún no se le ha extraído la información, el resultado es el archivo links_not_scaped.csv, el contenido de este archivo es el que se debe copiar y pegar en el archivo merged_links.csv y ejecutar de nuevo el paso 3
4. consolidate_offerts.py -> une todos los archivos ofertas-*.csv en uno solo para poder ser tratado más fácil
5. deduplicate_offers.py -> elimina duplicados, toma el campo link como referencia