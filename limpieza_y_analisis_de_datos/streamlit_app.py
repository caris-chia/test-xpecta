import pandas as pd
import streamlit as st
import folium
from streamlit_folium import folium_static
import plotly.express as px
import path
from st_aggrid import AgGrid, GridOptionsBuilder
import seaborn as sns
import matplotlib.pyplot as plt

base_dir=path.Path(__file__).absolute().parent

# Título de la aplicación
st.title('Apartamentos en venta en Bogotá D.C')

file_path = f"{base_dir}/cleaned_data_for_regression.csv"
df = pd.read_csv(file_path)

st.write('El análisis del costo de los apartamentos a la venta en Bogotá es de gran relevancia, ya que contribuye a comprender las dinámicas del mercado inmobiliario en una de las ciudades más importantes de Colombia. Esta información no solo es fundamental para potenciales compradores, sino también para inversores y planificadores urbanos que buscan identificar tendencias y evaluar la accesibilidad de la vivienda en la capital. En concordancia, según Garay y Rodríguez (2021), el comportamiento del mercado inmobiliario en Bogotá refleja aspectos económicos y sociales que impactan tanto en la calidad de vida de los residentes como en las estrategias de desarrollo urbano sostenible, por lo tanto, estudiar estas variables permite un entendimiento más profundo de cómo se configuran los precios y su relación con factores espaciales y socioeconómicos.La tabla a continuación muestra una lista detallada de apartamentos en venta dentro del área delimitada por la Carrera 30, la Calle 26, la Calle 72 y la Avenida Boyacá en Bogotá. Cada propiedad incluye información sobre el precio, la ubicación, el número de habitaciones, y más detalles para facilitar su análisis.')

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
    options=['precio', 'área_construida', 'baños', 'habitaciones', 'parqueaderos', 'estrato_social', 'precio_por_metro_cuadrado']
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
st.write('El siguiente mapa interactivo utiliza marcadores para indicar la ubicación de cada propiedad, dichos marcadores se encuentran distribuidos principalmente en una zona urbana, específicamente en localidades como Teusaquillo y sus alrededores, dentro de la ciudad. Por medio de las opciones de navegación como zoom se puede explorar diferentes niveles de detalle del área donde se encuentran ubicados dichos apartamentos para comprender el acceso a vías principales, parques metropolitanos, centros comerciales u otros lugares que valorizan las urbanizaciones.')

st.subheader('Mapa Interactivo de las Propiedades')
folium_static(m)

# Visualización descriptiva de la data
st.subheader('Análisis Descriptivo de diferentes variables')
st.write('Para la siguiente visualización con el filtro que se encuentra a la izquierda de la pantalla, se puede explorar diferentes análisis descriptivos de las variables que contiene la base de datos. En términos de precios, la mayor concentración está en el rango de 0.4B, con algunos valores atípicos que alcanzan hasta 1.2B. La distribución del área construida muestra que la mayoría de las propiedades tienen entre 50 y 100 metros cuadrados, siendo menos comunes las áreas mayores a 150 m². En cuanto a la cantidad de baños y habitaciones, se observa que la mayoría de las propiedades tienen 2 baños y 3 habitaciones respectivamente, lo cual es consistente con propiedades de tamaño medio orientadas a familias. En cuanto a parqueaderos, la mayoría de las propiedades tienen uno, lo cual era de esperarse ya que son propiedades urbanas. La distribución del estrato social muestra que el estrato 4 es el más común, seguido por el estrato 5, lo que podría sugerir que estas propiedades se encuentran en áreas de clase media-alta y las propiedades de menor estrato no suelen ser publicadas en inmobiliarias ni bases de datos como Finca Raiz. Finalmente, la distribución del precio por metro cuadrado varía entre 4 Millones de pesos colombianos y 8 Millones de pesos colombianos, lo cual refleja una variabilidad importante en el costo dependiendo de la ubicación y características específicas de cada propiedad.')

# Mostrar estadísticas descriptivas generales para la variable seleccionada
st.write(f"Estadísticas descriptivas para {selected_variable}:")
st.write(filtered_df[selected_variable].describe())

# Histograma de la variable seleccionada
st.subheader(f'Distribución de {selected_variable}')
fig = px.histogram(filtered_df, x=selected_variable, nbins=30, title=f'Distribución de {selected_variable}')

# Ajustar el eje X para que muestre solo números enteros si corresponde a ciertas variables
if selected_variable in ['baños', 'habitaciones', 'parqueaderos', 'estrato_social']:
    fig.update_xaxes(dtick=1)

st.plotly_chart(fig)


# Gráfico de dispersión de área construida vs. precio
st.subheader('Relación entre Área Construida y Precio')
fig = px.scatter(filtered_df, x='área_construida', y='precio', title='Relación entre Área Construida y Precio', labels={'área_construida': 'Área Construida', 'precio': 'Precio'})
st.plotly_chart(fig)

# Top 5 de barrios más costosos y más económicos por metro cuadrado
st.subheader('Top 5 de Barrios Más Costosos y Más Económicos (por Metro Cuadrado)')

# Agrupar por ubicación principal y calcular el precio promedio por metro cuadrado
average_price_per_sqm_per_location = filtered_df.groupby('ubicación_principal')['precio_por_metro_cuadrado'].mean().reset_index()

# Top 5 barrios más costosos por metro cuadrado
top_5_expensive_sqm = average_price_per_sqm_per_location.nlargest(5, 'precio_por_metro_cuadrado')
fig = px.bar(top_5_expensive_sqm, x='ubicación_principal', y='precio_por_metro_cuadrado', title='Top 5 Barrios Más Costosos por Metro Cuadrado', labels={'ubicación_principal': 'Barrio', 'precio_por_metro_cuadrado': 'Precio Promedio por Metro Cuadrado'})
st.write('En la siguiente gráfica se muestra el top 5 de barrios más costosos por metro cuadrado. Podemos observar que "Ciudad Salitre" es el barrio con el precio más alto por metro cuadrado, seguido por "El Salitre". Los barrios como "Modelia", "Zona Chapinero", y "Los Rosales" también presentan altos valores, lo que evidencia alta demanda en el mercado inmobiliario. Estos barrios suelen estar ubicados en zonas de alta demanda debido a factores como la ubicación estratégica, el acceso a servicios y comodidades, así como un ambiente atractivo que justifica el precio.')
st.plotly_chart(fig)

# Top 5 barrios más económicos por metro cuadrado
top_5_cheap_sqm = average_price_per_sqm_per_location.nsmallest(5, 'precio_por_metro_cuadrado')
fig = px.bar(top_5_cheap_sqm, x='ubicación_principal', y='precio_por_metro_cuadrado', title='Top 5 Barrios Más Económicos por Metro Cuadrado', labels={'ubicación_principal': 'Barrio', 'precio_por_metro_cuadrado': 'Precio Promedio por Metro Cuadrado'})
st.write('Respecto al top 5 de barrios más económicos por metro cuadrado, Acapulco encabeza la lista con un costo promedio de 4 millones de pesos colombuanos, sin embargo, los barrios como Bosque Popular, Pablo VI y la esmeralda se encuentran en rangos similares que no superan los 4.7 millones de pesos.')
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
st.write('El mapa de calor muestra las correlaciones entre distintas variables numéricas del conjunto de datos sobre propiedades. La correlación se mide con valores entre -1 y 1, donde valores cercanos a 1 indican una fuerte correlación positiva, valores cercanos a -1 indican una fuerte correlación negativa, y valores cercanos a 0 indican una débil o nula relación.\n\nPrecio y Área Construida: Existe una correlación positiva significativa de 0.67, lo cual sugiere que el precio de las propiedades tiende a aumentar a medida que el área construida aumenta.\n\nPrecio y Baños: La correlación es de 0.55, indicando una relación moderada, donde un mayor número de baños también se asocia con un incremento en el precio.\n\nÁrea Construida y Baños: La correlación entre estas variables es de 0.62, lo cual muestra que el área construida tiene una relación considerable con la cantidad de baños, sugiriendo que las propiedades más grandes tienden a tener más baños.\n\nPrecio y Parqueaderos: Hay una correlación de 0.62 entre el precio y la cantidad de parqueaderos, lo cual indica que las propiedades con más parqueaderos suelen tener precios más altos.\n\nÁrea Privada: Esta variable tiene correlaciones bajas con la mayoría de las otras variables, indicando que no tiene una relación significativa con el precio, el área construida o el número de baños.\n\nPrecio por Metro Cuadrado y Área Construida: Existe una correlación negativa de -0.44, lo que implica que, a medida que el área construida aumenta, el precio por metro cuadrado tiende a disminuir, probablemente debido a economías de escala.\n\nHabitaciones: La correlación entre el número de habitaciones y otras variables, como el precio (0.31) y el área construida (0.59), indica que, aunque hay una cierta relación positiva, no es tan fuerte como con otras características.')
correlation_matrix = filtered_df[['precio', 'área_construida', 'área_privada', 'baños', 'habitaciones', 'parqueaderos', 'precio_por_metro_cuadrado']].corr()
fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', ax=ax)
st.pyplot(fig)

# Frecuencia de propiedades en el mercado por barrio
st.subheader('Frecuencia de Propiedades en el Mercado por Barrio')
st.write('La siguiente gráfica muestra la distribución de la cantidad de apartamentos disponibles para la venta en diferentes barrios de Bogotá. Se destaca una fuerte concentración de ofertas en el barrio Nicolás de Federmán, seguido por barrios como Normandía y Engativá. La distribución tiene varia significativamente, con una notable caída en el número de registros después de los primeros barrios y una larga cola de zonas con muy pocas ofertas donde puede haber oportunidad de oferta.')
property_count_per_location = filtered_df['ubicación_principal'].value_counts().reset_index()
property_count_per_location.columns = ['Barrio', 'Cantidad de Propiedades']
fig = px.bar(property_count_per_location, x='Barrio', y='Cantidad de Propiedades', title='Cantidad de Propiedades por Barrio', labels={'Barrio': 'Barrio', 'Cantidad de Propiedades': 'Cantidad'})
st.plotly_chart(fig)
