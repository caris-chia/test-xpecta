import pandas as pd
import streamlit as st
import folium
from streamlit_folium import folium_static
import plotly.express as px
import path
import sys
from st_aggrid import AgGrid, GridOptionsBuilder
import seaborn as sns
import matplotlib.pyplot as plt

base_dir=path.Path(__file__).absolute().parent

# Título de la aplicación
st.title('Apartamentos en venta en Bogotá D.C')

file_path = f"{base_dir}/cleaned_data_for_regression.csv"
df = pd.read_csv(file_path)

st.write('La tabla a continuación muestra una lista detallada de apartamentos en venta dentro del área delimitada por la Carrera 30, la Calle 26, la Calle 72 y la Avenida Boyacá en Bogotá. Cada propiedad incluye información sobre el precio, la ubicación, el número de habitaciones, y más detalles para facilitar su análisis.')

# Renombrar las columnas a español
df.rename(columns={
    'state': 'estado',
    'age': 'antigüedad',
    'administration': 'costo_administración',
    'floor_number': 'número_de_piso',
    'price': 'precio',
    'constructed_area': 'área_construida',
    'private_area': 'área_privada',
    'bathrooms': 'baños',
    'rooms': 'habitaciones',
    'parking_spaces': 'parqueaderos',
    'social_stratum': 'estrato_social',
    'price_per_sqm': 'precio_por_metro_cuadrado',
    'main_location': 'ubicación_principal',
    'address': 'dirección',
    'link': 'enlace',
    'finca_raiz_id': 'id_finca_raiz'
}, inplace=True)

# Filtrar datos donde 'in_polygon' es igual a 1
df['ubicación_principal'] = df['ubicación_principal'].str.replace('Bogotá, .*', '', regex=True).str.replace(',', '').str.strip()

filtered_df = df[df['in_polygon'] == 1]

# Eliminar outliers basados en el área construida y precio
filtered_df = filtered_df[(filtered_df['área_construida'] < 500) & (filtered_df['precio'] < filtered_df['precio'].quantile(0.95)) & (filtered_df['precio'] > filtered_df['precio'].quantile(0.05))]

# Agregar columna de precio por metro cuadrado
filtered_df['precio_por_metro_cuadrado'] = filtered_df['precio'] / filtered_df['área_construida']

# Reorganizar las columnas como se solicitó
columns_order = ['id_finca_raiz', 'enlace', 'precio', 'ubicación_principal', 'dirección'] + [col for col in filtered_df.columns if col not in ['id_finca_raiz', 'enlace', 'precio', 'ubicación_principal', 'dirección']]
filtered_df = filtered_df[columns_order]

# Sidebar para seleccionar variable a analizar
st.sidebar.header('Configuración de Visualización')
selected_variable = st.sidebar.selectbox(
    'Seleccione la variable para el análisis descriptivo:',
    options=['precio', 'área_construida', 'área_privada', 'baños', 'habitaciones', 'parqueaderos', 'estrato_social', 'precio_por_metro_cuadrado']
)

# Mostrar el DataFrame filtrado con opciones de filtrado interactivo

# Configurar AgGrid para la tabla interactiva
gb = GridOptionsBuilder.from_dataframe(filtered_df)
gb.configure_pagination(paginationAutoPageSize=True)
gb.configure_side_bar()
gb.configure_default_column(editable=True, filter=True, headerCheckboxSelection=True)
# Personalizar encabezados de columnas
gb.configure_column('id_finca_raiz', header_name='ID Finca Raíz')
gb.configure_column('enlace', header_name='Enlace')
gb.configure_column('precio', header_name='Precio')
gb.configure_column('ubicación_principal', header_name='Ubicación Principal')
gb.configure_column('dirección', header_name='Dirección')
gb.configure_column('antigüedad', header_name='Antigüedad')
gb.configure_column('costo_administración', header_name='Costo Administración')
gb.configure_column('número_de_piso', header_name='Número de Piso')
gb.configure_pagination(paginationAutoPageSize=True)
gb.configure_side_bar()
gb.configure_default_column(editable=True, filter=True)
grid_options = gb.build()

AgGrid(filtered_df, gridOptions=grid_options, enable_enterprise_modules=True)

# Crear el mapa centrado en las coordenadas promedio
avg_lat = filtered_df['coordinates_lat'].mean()
avg_lng = filtered_df['coordinates_lng'].mean()

m = folium.Map(location=[avg_lat, avg_lng], zoom_start=12)

# Agregar puntos al mapa
for _, row in filtered_df.iterrows():
    folium.Marker(
        location=[row['coordinates_lat'], row['coordinates_lng']],
        popup=row['dirección']
    ).add_to(m)

# Mostrar el mapa interactivo
    
st.subheader('Mapa Interactivo de las Propiedades')
folium_static(m)

# Mostrar el DataFrame filtrado con opciones de filtrado interactivo
st.subheader('Apartamentos en venta entre la Carrera 30, la Calle 26, la Calle 72 y la Avenida Boyacá')
# Visualización descriptiva de la data
st.subheader('Análisis Descriptivo de la Variable Seleccionada')

# Mostrar estadísticas descriptivas generales para la variable seleccionada
st.write(f"Estadísticas descriptivas para {selected_variable}:")
st.write(filtered_df[selected_variable].describe())

# Histograma de la variable seleccionada
st.subheader(f'Distribución de {selected_variable}')
fig = px.histogram(filtered_df, x=selected_variable, nbins=30, title=f'Distribución de {selected_variable}')
st.plotly_chart(fig)

# Gráfico de dispersión de área construida vs. precio
st.subheader('Relación entre Área Construida y Precio')
fig = px.scatter(filtered_df, x='área_construida', y='precio', title='Relación entre Área Construida y Precio', labels={'área_construida': 'Área Construida', 'precio': 'Precio'})
st.plotly_chart(fig)

# Gráfico de barras de estrato social
st.subheader('Distribución del Estrato Social')

# Obtener la distribución del estrato social y ajustar los nombres de columna
social_stratum_counts = filtered_df['estrato_social'].value_counts().reset_index()
social_stratum_counts.columns = ['Estrato Social', 'Cantidad']

# Crear el gráfico de barras con los nombres de columna corregidos
fig = px.bar(social_stratum_counts, x='Estrato Social', y='Cantidad', title='Distribución del Estrato Social')
st.plotly_chart(fig)

# Top 5 de barrios más costosos y más económicos por metro cuadrado
st.subheader('Top 5 de Barrios Más Costosos y Más Económicos (por Metro Cuadrado)')

# Agrupar por ubicación principal y calcular el precio promedio por metro cuadrado
average_price_per_sqm_per_location = filtered_df.groupby('ubicación_principal')['precio_por_metro_cuadrado'].mean().reset_index()

# Top 5 barrios más costosos por metro cuadrado
top_5_expensive_sqm = average_price_per_sqm_per_location.nlargest(5, 'precio_por_metro_cuadrado')
fig = px.bar(top_5_expensive_sqm, x='ubicación_principal', y='precio_por_metro_cuadrado', title='Top 5 Barrios Más Costosos por Metro Cuadrado', labels={'ubicación_principal': 'Barrio', 'precio_por_metro_cuadrado': 'Precio Promedio por Metro Cuadrado'})
st.write('En la siguiente gráfica se muestra el top 5 de barrios más costosos por metro cuadrado. Podemos observar que "Ciudad Salitre" es el barrio con el precio más alto por metro cuadrado, seguido muy de cerca por "El Salitre". Los barrios como "Modelia", "Zona Chapinero", y "Los Rosales" también presentan altos valores, lo cual refleja su atractivo y demanda en el mercado inmobiliario. Estos barrios suelen estar ubicados en zonas de alta demanda debido a factores como la ubicación estratégica, el acceso a servicios y comodidades, así como un ambiente atractivo que justifica el precio.')
st.plotly_chart(fig)

# Top 5 barrios más económicos por metro cuadrado
top_5_cheap_sqm = average_price_per_sqm_per_location.nsmallest(5, 'precio_por_metro_cuadrado')
fig = px.bar(top_5_cheap_sqm, x='ubicación_principal', y='precio_por_metro_cuadrado', title='Top 5 Barrios Más Económicos por Metro Cuadrado', labels={'ubicación_principal': 'Barrio', 'precio_por_metro_cuadrado': 'Precio Promedio por Metro Cuadrado'})
st.write('En la siguiente gráfica se muestra el top 5 de barrios más económicos por metro cuadrado. Estos barrios, al tener precios más accesibles, pueden ofrecer oportunidades atractivas para aquellos compradores que buscan una relación calidad-precio más asequible. Los bajos precios pueden deberse a una menor demanda, la disponibilidad de servicios o la localización en zonas menos concurridas en comparación con los barrios más costosos. Esta información puede ser útil para aquellos que buscan alternativas económicas dentro del mercado inmobiliario de Bogotá.')
st.plotly_chart(fig)

# Distribución geográfica del precio por metro cuadrado
st.subheader('Distribución Geográfica del Precio por Metro Cuadrado')
folium_map = folium.Map(location=[avg_lat, avg_lng], zoom_start=12)
for _, row in average_price_per_sqm_per_location.iterrows():
    folium.CircleMarker(
        location=[filtered_df[filtered_df['ubicación_principal'] == row['ubicación_principal']]['coordinates_lat'].mean(),
                 filtered_df[filtered_df['ubicación_principal'] == row['ubicación_principal']]['coordinates_lng'].mean()],
        radius=10,
        color='blue',
        fill=True,
        fill_color='blue',
        fill_opacity=0.6,
        popup=f"{row['ubicación_principal']}: ${row['precio_por_metro_cuadrado']:.2f} por m²"
    ).add_to(folium_map)
folium_static(folium_map)

# Análisis de correlación entre variables numéricas
st.subheader('Mapa de Calor de Correlaciones entre Variables Numéricas')
correlation_matrix = filtered_df[['precio', 'área_construida', 'área_privada', 'baños', 'habitaciones', 'parqueaderos', 'precio_por_metro_cuadrado']].corr()
fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', ax=ax)
st.pyplot(fig)

# Frecuencia de propiedades en el mercado por barrio
st.subheader('Frecuencia de Propiedades en el Mercado por Barrio')
property_count_per_location = filtered_df['ubicación_principal'].value_counts().reset_index()
property_count_per_location.columns = ['Barrio', 'Cantidad de Propiedades']
fig = px.bar(property_count_per_location, x='Barrio', y='Cantidad de Propiedades', title='Cantidad de Propiedades por Barrio', labels={'Barrio': 'Barrio', 'Cantidad de Propiedades': 'Cantidad'})
st.plotly_chart(fig)

# Nota: Asegúrate de tener los siguientes paquetes instalados:
# streamlit, pandas, folium, streamlit-folium, plotly, streamlit-aggrid, seaborn, matplotlib
# Puedes instalarlos con: pip install streamlit pandas folium streamlit-folium plotly streamlit-aggrid seaborn matplotlib
