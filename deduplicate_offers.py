import pandas as pd

# Cargar el archivo offers.csv en un DataFrame
df = pd.read_csv("./output/offers.csv")

# Eliminar duplicados basados en el campo 'link', manteniendo solo la primera aparición
df_deduplicated = df.drop_duplicates(subset='link', keep='first')

# Guardar los registros únicos en un nuevo archivo CSV
df_deduplicated.to_csv("./output/offers_deduplicated.csv", index=False)

print("Archivo deduplicado guardado como offers_deduplicated.csv")