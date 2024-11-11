import pandas as pd

# Cargar el archivo CSV en un DataFrame
df = pd.read_csv("./merged_links/merged_links_20241110_215909.csv")

# Filtrar los registros donde la columna 'scraped_at' está vacía
# Usamos isna() para NaN y el operador | para incluir las cadenas vacías
filtered_df = df[df['scraped_at'].isna() | (df['scraped_at'] == "")]

# Mostrar los resultados
# print(filtered_df)

# Opcional: Guardar los registros filtrados en un nuevo archivo CSV
filtered_df.to_csv("./output/links_not_scaped.csv", index=False)