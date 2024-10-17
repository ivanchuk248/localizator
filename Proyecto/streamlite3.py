#streamlit run streamlite3.py

import streamlit as st
import pandas as pd
import psycopg2
import folium
from geopy.geocoders import Nominatim
import requests
from matplotlib import pyplot as plt
import seaborn as sns
from streamlit_folium import st_folium

# Datos de conexión a PostgreSQL
db_host = "brmifmitysqdshmrmblh-postgresql.services.clever-cloud.com"
db_name = "brmifmitysqdshmrmblh"
db_user = "uz5x38eqwuqxrodugfcb"
db_port = 50013
db_password = "SaTxVrCVimar29oRIFYTv3uYLaRf4B"

# Función para conectarse a la base de datos
def conectar_db():
    conn = psycopg2.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=db_password,
        port=db_port
    )
    return conn

# Función para cargar datos de la tabla locales
def cargar_datos():
    conn = conectar_db()
    query = "SELECT * FROM locales"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Cargar los datos
data = cargar_datos()


def extraer_ubicacion(direccion):
    # Encontrar la primera coma y dividir la cadena
    parte_antes_coma = direccion.split(',')[0].strip()

    # Añadir 'Bogotá' a la parte extraída
    ubicacion_simplificada = f"{parte_antes_coma}, Bogotá"

    return ubicacion_simplificada





def despliegue_mapa(lugar):
    lugar=extraer_ubicacion(lugar)
    st.header("Mapa de Venecia, Tunjuelito y Lugares de Interés")

    # Crear un geocodificador con un user_agent único
    geolocator = Nominatim(user_agent="mi_aplicacion_geocodificacion_v1.0")

    # Dirección a geocodificar
    #direccion = "venecia, tunjuelito"
    direccion = lugar

    # Obtener la ubicación
    ubicacion_geo = geolocator.geocode(direccion)

    if ubicacion_geo:
        # Coordenadas de la ubicación
        latitud = ubicacion_geo.latitude
        longitud = ubicacion_geo.longitude

        # Crear un mapa centrado en la ubicación
        mapa = folium.Map(location=[latitud, longitud], zoom_start=14)

        # Agregar un marcador en la ubicación
        folium.Marker(
            location=[latitud, longitud],
            popup=direccion,
            icon=folium.Icon(color='blue')
        ).add_to(mapa)

        # Realizar una consulta a Overpass API para lugares de interés
        query = f"""
        [out:json];
        (
          node["amenity"](around:1000, {latitud}, {longitud});
          way["amenity"](around:1000, {latitud}, {longitud});
          relation["amenity"](around:1000, {latitud}, {longitud});
        );
        out body;
        """
        overpass_url = "http://overpass-api.de/api/interpreter"
        response = requests.get(overpass_url, params={'data': query})
        data_overpass = response.json()

        # Crear una lista para almacenar los lugares y sus datos
        lugares_interes = []

        # Agregar lugares de interés al mapa y a la lista
        for element in data_overpass['elements']:
            if 'tags' in element:
                # Extraer información básica
                name = element['tags'].get('name', 'Sin nombre')
                amenity = element['tags'].get('amenity', 'Desconocido')
                address = element['tags'].get('address', 'Sin dirección')
                website = element['tags'].get('website', 'Sin sitio web')
                opening_hours = element['tags'].get('opening_hours', 'Sin horario de apertura')

                if 'lat' in element and 'lon' in element:
                    # Agregar un marcador en el mapa
                    folium.Marker(
                        location=[element['lat'], element['lon']],
                        popup=f"<strong>{name}</strong><br>Tipo: {amenity}<br>Dirección: {address}<br>Sitio Web: {website}<br>Horario: {opening_hours}",
                        icon=folium.Icon(color='green')
                    ).add_to(mapa)

                    # Agregar a la lista
                    lugares_interes.append({
                        'Lugar': name,
                        'Tipología': amenity,
                        'Dirección': address,
                        'Sitio Web': website,
                        'Horario': opening_hours
                    })

        # Crear un DataFrame con los lugares de interés
        df_lugares = pd.DataFrame(lugares_interes)

        # Mostrar el DataFrame en Streamlit
        st.subheader("Lugares de Interés")
        st.dataframe(df_lugares)

        # Mostrar el mapa en Streamlit
        st.subheader("Mapa con Lugares de Interés")
        st_folium(mapa, width=700, height=500)
    else:
        st.write("La dirección no se pudo geocodificar.")

# Asegurarse de que la columna 'precio' sea del tipo correcto
data['precio'] = data['precio'].replace(',', '', regex=True).astype(float)

# ------------------------------------------------------------------------------------------
# Título de la aplicación
st.title("Lista de Locales en Bogotá")

# Opciones de filtrado
st.sidebar.header("Filtrar resultados")

# Filtros de ubicación, tipo de operación y agencia
ubicacion = st.sidebar.selectbox("Seleccionar ubicación:", options=["Todas"] + list(data['ubicacion'].unique()))
tipo_operacion = st.sidebar.selectbox("Seleccionar tipo de operación:", options=["Todas"] + list(data['operacion'].unique()))
agencia = st.sidebar.selectbox("Seleccionar agencia:", options=["Todas"] + list(data['agencia'].unique()))

# Aplicar filtros de ubicación, tipo de operación y agencia
if ubicacion != "Todas":
    data = data[data['ubicacion'] == ubicacion]
    despliegue_mapa(ubicacion)

if tipo_operacion != "Todas":
    data = data[data['operacion'] == tipo_operacion]

if agencia != "Todas":
    data = data[data['agencia'] == agencia]

# Rango de precios (utiliza un slider)
st.sidebar.header("Filtrar por precio")
min_precio = int(data['precio'].min())
max_precio = int(data['precio'].max())

precio_seleccionado = st.sidebar.slider(
    "Seleccionar rango de precio:",
    min_value=min_precio,
    max_value=max_precio,
    value=(min_precio, max_precio)
)

# Aplicar filtro de rango de precios
data = data[(data['precio'] >= precio_seleccionado[0]) & (data['precio'] <= precio_seleccionado[1])]

# Selector para ordenar por precio
st.sidebar.header("Ordenar por precio")
orden_precio = st.sidebar.radio(
    "Ordenar precios:",
    ("Ascendente", "Descendente")
)

# Aplicar orden de precios
if orden_precio == "Ascendente":
    data = data.sort_values(by='precio', ascending=True)
else:
    data = data.sort_values(by='precio', ascending=False)

# Mostrar la tabla con los resultados
st.write("### Resultados:")
st.dataframe(data)

# Asegurarse de que el campo 'imagen_url' está presente y contiene URLs válidas
if 'imagen_url' in data.columns:
    # Crear una nueva columna en el DataFrame con las imágenes renderizadas usando HTML
    data['Imagen'] = data['imagen_url'].apply(lambda url: f'<img src="{url}" width="100" height="100">')

    # Mostrar el DataFrame con la columna de imágenes en Streamlit
    st.write("### Resultados con Imágenes:")
    st.write(data[['Imagen', 'ubicacion', 'precio', 'operacion', 'agencia','enlace']].to_html(escape=False), unsafe_allow_html=True)

# Opcional: mostrar estadísticas o gráficos adicionales
st.sidebar.header("Estadísticas")
st.sidebar.write("Número total de locales:", len(data))

# Título de la aplicación para el mapa




#despliegue_mapa()

# ------------------------------------------------------------------------------------------
# Agregar Gráficos al Final de la Aplicación
st.header("Análisis de Datos")

# 1. Distribución de Precios
if st.button("Mostrar Distribución de Precios"):
    st.subheader("Distribución de Precios")
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    sns.histplot(data['precio'], bins=30, kde=True, color='skyblue', ax=ax1)
    ax1.set_title('Distribución de Precios de Locales', fontsize=16)
    ax1.set_xlabel('Precio', fontsize=14)
    ax1.set_ylabel('Frecuencia', fontsize=14)
    st.pyplot(fig1)
# 2. Precio Promedio por Ubicación
if st.sidebar.button("Mostrar Precio Promedio por Ubicación"):
    st.subheader("Precio Promedio por Ubicación")
    avg_price_location = data.groupby('ubicacion')['precio'].mean().reset_index()
    fig2, ax2 = plt.subplots(figsize=(12, 8))
    sns.barplot(x='precio', y='ubicacion', data=avg_price_location, palette='viridis', ax=ax2)
    ax2.set_title('Precio Promedio por Ubicación', fontsize=16)
    ax2.set_xlabel('Precio Promedio', fontsize=14)
    ax2.set_ylabel('Ubicación', fontsize=14)
    st.pyplot(fig2)

# 3. Número de Locales por Agencia
st.subheader("Número de Locales por Agencia")
count_agencia = data['agencia'].value_counts().reset_index()
count_agencia.columns = ['agencia', 'cantidad']
fig3, ax3 = plt.subplots(figsize=(12, 8))
sns.barplot(x='cantidad', y='agencia', data=count_agencia, palette='magma', ax=ax3)
ax3.set_title('Número de Locales por Agencia', fontsize=16)
ax3.set_xlabel('Cantidad de Locales', fontsize=14)
ax3.set_ylabel('Agencia', fontsize=14)
st.pyplot(fig3)


