import pandas as pd
from datetime import datetime

# Cargar los archivos CSV en DataFrames
df_a = pd.read_csv("./ofertas/ofertas-1731292214.670988.csv")
df_b = pd.read_csv("./merged_links/merged_links_20241110_212330.csv")

# Asegurarse de que la columna 'scraped_at' en df_b esté en formato string
df_b['scraped_at'] = df_b['scraped_at'].astype(str)

# Filtrar los registros de df_b cuyos links están en df_a
filtered_indices = df_b['link'].isin(df_a['link'])

# Agregar un timestamp en la columna scraped_at para los registros filtrados
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
df_b.loc[filtered_indices, 'scraped_at'] = timestamp

# Reemplazar los valores 'nan' en 'scraped_at' con una cadena vacía
df_b['scraped_at'] = df_b['scraped_at'].replace("nan", "")

# Guardar el archivo B actualizado con un nombre que incluya el timestamp
df_b.to_csv(f"./merged_links/merged_links_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", index=False)

print("Archivo B actualizado con el timestamp en los registros que existen en A.")