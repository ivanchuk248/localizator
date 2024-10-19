import streamlit as st
import pandas as pd
import psycopg2
import folium
from geopy.geocoders import Nominatim
import requests
from matplotlib import pyplot as plt
import seaborn as sns
from streamlit_folium import st_folium

# URL del logo en el sidebar
logo_url_sidebar = "https://talentotech.gov.co/849/articles-334606_foto_marquesina.jpg"
st.sidebar.image(logo_url_sidebar, width=200)



# Crear un menú lateral
pagina = st.sidebar.selectbox("Selecciona una página", ["Inicio", "Mapas"])
# Redirigir a la página correspondiente


if pagina == "Mapas":
    import mapas

# Datos de conexión a PostgreSQL
db_host = "brmifmitysqdshmrmblh-postgresql.services.clever-cloud.com"
db_name = "brmifmitysqdshmrmblh"
db_user = "uz5x38eqwuqxrodugfcb"
db_port = 50013
db_password = "SaTxVrCVimar29oRIFYTv3uYLaRf4B"

# Función para conectarse a la base de datos PostgreSQL
def conectar_db():
    try:
        conn = psycopg2.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password,
            port=db_port
        )
        return conn
    except Exception as e:
        st.error(f"Error al conectar a la base de datos: {e}")
        return None




# Función para cargar los datos de la tabla 'locales'
def cargar_datos():
    conn = conectar_db()
    if conn:
        try:
            query = "SELECT * FROM locales"
            df = pd.read_sql(query, conn)
            conn.close()
            return df
        except Exception as e:
            st.error(f"Error al cargar datos: {e}")
            return pd.DataFrame()  # Retornar un DataFrame vacío en caso de error
    else:
        return pd.DataFrame()

# Función para simplificar la dirección para la geocodificación
def extraer_ubicacion(direccion):
    return f"{direccion.split(',')[0].strip()}, Bogotá"

# Función para desplegar el mapa con lugares de interés cercanos
def obtener_color_y_icono(amenity):
    """Devuelve un color y un ícono según la tipología de amenidad."""
    amenities = {
        "restaurant": ('red', 'cutlery'),
        "pharmacy": ('blue', 'medkit'),
        "fast_food": ('orange', 'fast-food'),
        "post_office": ('green', 'envelope'),
        "school": ('lightblue', 'graduation-cap'),
        "cafe": ('brown', 'coffee'),
        "dentist": ('pink', 'tooth'),
        "bar": ('purple', 'beer'),
        "parking_entrance": ('gray', 'car'),
        "place_of_worship": ('gold', 'cross'),
        "bank": ('navy', 'credit-card'),
        "shelter": ('orange', 'home'),
        "hospital": ('red', 'hospital-o'),
        "marketplace": ('lightgreen', 'shopping-cart'),
        "parking": ('gray', 'car'),
        "veterinary": ('lightpink', 'paw'),
        "police": ('darkblue', 'shield'),
        "townhall": ('brown', 'town-hall'),
        "waste_basket": ('darkgreen', 'trash'),
        "juice_bar": ('yellow', 'glass'),
        "casino": ('purple', 'gambling'),
        "recycling": ('teal', 'recycle'),
        "childcare": ('lightcoral', 'child'),
        "pub": ('orange', 'beer'),
        "internet_cafe": ('lightblue', 'internet'),
        "post_depot": ('lightgray', 'package'),
        "atm": ('darkgray', 'money'),
    }

    return amenities.get(amenity, ('gray', 'question-circle'))  # Color e ícono por defecto para otros tipos


def despliegue_mapa(lugar):
    lugar = extraer_ubicacion(lugar)
    st.header("Mapa de " + lugar)

    geolocator = Nominatim(user_agent="mi_aplicacion_geocodificacion_v1.0")

    try:
        ubicacion_geo = geolocator.geocode(lugar)
        if not ubicacion_geo:
            st.error("La dirección no se pudo geocodificar.")
            return
    except Exception as e:
        st.error(f"Error en la geocodificación: {e}")
        return

    latitud, longitud = ubicacion_geo.latitude, ubicacion_geo.longitude
    mapa = folium.Map(location=[latitud, longitud], zoom_start=14)

    # Agregar marcador principal
    folium.Marker(
        location=[latitud, longitud],
        popup=lugar,
        icon=folium.Icon(color='blue')
    ).add_to(mapa)

    # Consulta a Overpass API para obtener lugares de interés
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

    try:
        response = requests.get(overpass_url, params={'data': query})
        data_overpass = response.json()
    except Exception as e:
        st.error(f"Error al consultar Overpass API: {e}")
        return

    # Procesar lugares de interés
    lugares_interes = []
    for element in data_overpass.get('elements', []):
        if 'tags' in element:
            name = element['tags'].get('name', 'Sin nombre')
            amenity = element['tags'].get('amenity', 'Desconocido')
            address = element['tags'].get('address', 'Sin dirección')
            website = element['tags'].get('website', 'Sin sitio web')
            opening_hours = element['tags'].get('opening_hours', 'Sin horario de apertura')

            if 'lat' in element and 'lon' in element:
                # Obtener color e ícono según la tipología
                color, icon = obtener_color_y_icono(amenity)

                folium.Marker(
                    location=[element['lat'], element['lon']],
                    popup=f"<strong>{name}</strong><br>Tipo: {amenity}<br>Dirección: {address}<br>Sitio Web: {website}<br>Horario: {opening_hours}",
                    icon=folium.Icon(color=color, icon=icon)
                ).add_to(mapa)

                lugares_interes.append({
                    'Lugar': name,
                    'Tipología': amenity,
                    'Dirección': address,
                    'Sitio Web': website,
                    'Horario': opening_hours
                })

    # Mostrar lugares de interés en una tabla
    if lugares_interes:
        df_lugares = pd.DataFrame(lugares_interes)
        st.subheader("Lugares de Interés")
        st.dataframe(df_lugares)

        # Resumen de lugares de interés
        resumen = df_lugares['Tipología'].value_counts()
        st.subheader("Categorías")
        st.dataframe(resumen)

    st.subheader("Mapa con Lugares de Interés")
    st_folium(mapa, width=700, height=500)


# Cargar los datos de la tabla 'locales'
data = cargar_datos()

# Asegurarse de que la columna 'precio' esté en formato numérico
if 'precio' in data.columns:
    data['precio'] = data['precio'].replace(',', '', regex=True).astype(float)

# Asegurarse de que la columna 'area' esté en formato numérico
if 'area' in data.columns:
    # Reemplazar comas y puntos en la columna 'area'
    data['area'] = data['area'].replace({',': '', '\.': ''}, regex=True)

    # Convertir a float, usando pd.to_numeric con errors='coerce' para manejar los valores no numéricos
    data['area'] = pd.to_numeric(data['area'], errors='coerce')


# ------------------------------------------------------------------------------------------
# Sección de la interfaz de usuario (sidebar y contenido principal)
st.sidebar.header("Filtrar resultados")

# Filtros de ubicación, tipo de operación y agencia
ubicacion = st.sidebar.selectbox("Seleccionar ubicación:", options=["Todas"] + list(data['ubicacion'].unique()))
tipo_operacion = st.sidebar.selectbox("Seleccionar tipo de operación:", options=["Todas"] + list(data['operacion'].unique()))
agencia = st.sidebar.selectbox("Seleccionar agencia:", options=["Todas"] + list(data['agencia'].unique()))

# Logo principal
logo_url_main = "https://logowik.com/content/uploads/images/t_camara-de-comercio-de-bogota3363.logowik.com.webp"
st.image(logo_url_main, width=300)

st.title("Lista de Locales en Bogotá")

# Mostrar el DataFrame completo (si se desea)
if st.button("Mostrar DataFrame Completo"):
    st.dataframe(data)

# Aplicar filtros de ubicación
def cardsfun(data):
    # Verificar si la columna 'imagen_url' existe para las tarjetas
    if 'imagen_url' in data.columns:
        num_tarjetas = len(data)

        # Crear contenedor para las tarjetas
        for i in range(0, num_tarjetas, 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < num_tarjetas:
                    row = data.iloc[i + j]
                    with cols[j]:
                        card_html = f"""
                        <div style="
                            border: 1px solid #ccc; 
                            border-radius: 8px; 
                            padding: 16px; 
                            margin: 10px; 
                            display: flex; 
                            flex-direction: column; 
                            align-items: center; 
                            text-align: center; /* Centra el texto */
                        ">
                            <img src="{row['imagen_url']}" width="100%" height="100" style="border-radius: 8px;">
                            <h4 style="margin: 8px 0;">{row['titulo']}</h4>
                            <p style="margin: 4px 0;">Ubicación: {row['ubicacion']}</p>
                            <p style="margin: 4px 0;">Precio: ${row['precio']}</p>
                            <p style="margin: 4px 0;">Operación: {row['operacion']}</p>
                            <p style="margin: 4px 0;">Agencia: {row['agencia']}</p>
                            <p style="margin: 4px 0;">Área: {row['area']} m²</p>
                            <a href="{row['enlace']}" target="_blank" style="color: blue; text-decoration: none;">Ver más</a>
                        </div>
                        """
                        # Muestra la tarjeta
                        st.markdown(card_html, unsafe_allow_html=True)

                        # Agregar un expander para la descripción
                        with st.expander("Descripción"):
                            st.write(f"Descripción de {row['descripcion']}")
    else:
        st.write("No se encontraron resultados con las imágenes disponibles.")



if ubicacion != "Todas":
    data = data[data['ubicacion'] == ubicacion]
    cardsfun(data)
    despliegue_mapa(ubicacion)

# Aplicar filtros de tipo de operación y agencia
if tipo_operacion != "Todas":
    data = data[data['operacion'] == tipo_operacion]

if agencia != "Todas":
    data = data[data['agencia'] == agencia]

# Filtro de precio (slider)
st.sidebar.header("Filtrar por precio")
min_precio, max_precio = int(data['precio'].min()), int(data['precio'].max())
precio_seleccionado = st.sidebar.slider("Seleccionar rango de precio:", min_precio, max_precio, (min_precio, max_precio))
data = data[(data['precio'] >= precio_seleccionado[0]) & (data['precio'] <= precio_seleccionado[1])]

# Filtro de área (slider)
st.sidebar.header("Filtrar por área (m²)")
min_area, max_area = int(data['area'].min()), int(data['area'].max())
area_seleccionada = st.sidebar.slider("Seleccionar rango de área:", min_area, max_area, (min_area, max_area))
data = data[(data['area'] >= area_seleccionada[0]) & (data['area'] <= area_seleccionada[1])]

# Ordenar por precio (ascendente o descendente)
st.sidebar.header("Ordenar por precio")
orden_precio = st.sidebar.radio("Ordenar precios:", ("Ascendente", "Descendente"))
data = data.sort_values(by='precio', ascending=(orden_precio == "Ascendente"))

# Mostrar resultados
st.write("### Resultados:")





# Llama a la función con el DataFrame 'data'
cardsfun(data)

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

# Contar el número de locales por agencia
count_agencia = data['agencia'].value_counts().reset_index()
count_agencia.columns = ['agencia', 'cantidad']

# Calcular la altura del gráfico en función del número de agencias (asumiendo 0.5 por agencia)
num_agencias = len(count_agencia)
altura = num_agencias * 0.5  # Ajustar 0.5 según necesites más o menos espacio por barra

# Crear la figura y el gráfico
fig3, ax3 = plt.subplots(figsize=(12, altura))  # El ancho sigue siendo 12, pero la altura es dinámica
sns.barplot(x='cantidad', y='agencia', data=count_agencia, palette='magma', ax=ax3)

# Configurar títulos y etiquetas
ax3.set_title('Número de Locales por Agencia', fontsize=16)
ax3.set_xlabel('Cantidad de Locales', fontsize=14)
ax3.set_ylabel('Agencia', fontsize=14)

# Mostrar la gráfica en Streamlit
st.pyplot(fig3)
