import pandas as pd
import folium
from folium.plugins import MarkerCluster
from geopy.geocoders import Nominatim
import time
import re
import streamlit as st
from streamlit_folium import folium_static
import os

# Función para limpiar la dirección
def limpiar_direccion(direccion):
    # Eliminar "Piso" y lo que le sigue
    direccion_limpia = re.sub(r',? Piso \d+', '', direccion)  # Elimina "Piso" seguido de un número
    return direccion_limpia

# Título de la aplicación
st.title("Geocodificación de Direcciones en Bogotá")

# Cargar el archivo Excel directamente
file_path = 'mercado.xlsx'  # Especificar la ruta del archivo
try:
    df = pd.read_excel(file_path)
except FileNotFoundError:
    st.error(f"No se encontró el archivo '{file_path}'. Asegúrate de que esté en el directorio.")
    st.stop()  # Detener la ejecución si no se encuentra el archivo

# Filtrar el DataFrame para incluir solo las filas con dirección no nula
df = df[df['Dirección'].notna()]

# Tomar los primeros 20 registros
df_10 = df.head(20)

# Crear un mapa centrado en Bogotá
mapa = folium.Map(location=[4.6101, -74.0817], zoom_start=12)  # Coordenadas aproximadas de Bogotá

# Crear un clúster de marcadores
marker_cluster = MarkerCluster().add_to(mapa)

# Inicializar el geocodificador
geolocator = Nominatim(user_agent="mi_geocodificador")

# Agregar marcadores al mapa para los primeros 20 registros
for index, row in df_10.iterrows():
    # Limpiar la dirección para quitar información de piso
    direccion = limpiar_direccion(f"{row['Dirección']}, Bogotá")

    try:
        # Intentar geocodificar la dirección
        location = geolocator.geocode(direccion, timeout=10)  # Timeout de 10 segundos
    except Exception as e:
        st.error(f"Error al geocodificar '{direccion}': {e}")
        continue  # Continuar con la siguiente dirección

    if location:
        folium.Marker(
            location=[location.latitude, location.longitude],
            popup=folium.Popup(f"""
                <strong>Compañía:</strong> {row['Compañía']}<br>
                <strong>Sector:</strong> {row['Sector (NAICS)']}<br>
                <strong>Teléfono:</strong> {row['Teléfono']}<br>
                <strong>Correo Electrónico:</strong> {row['Correo Electrónico']}<br>
                <strong>Página Web:</strong> <a href="{row['Página Web']}">{row['Página Web']}</a><br>
                <strong>Dirección:</strong> {direccion}
            """, max_width=300),
            icon=folium.Icon(color='blue')
        ).add_to(marker_cluster)
        st.success(f"Georeferenciado exitoso: {direccion}")
    else:
        st.warning(f"No se pudo geocodificar la dirección: {direccion}")

    # Pausa de 1 segundo entre solicitudes para evitar limitaciones
    time.sleep(1)

# Guardar el mapa en un archivo HTML
output_file = 'mapa_companias.html'
mapa.save(output_file)

# Mostrar el mapa en Streamlit
st.subheader("Mapa de Compañías")
folium_static(mapa)

# Enlace para descargar el mapa
if os.path.exists(output_file):
    with open(output_file, "rb") as f:
        st.download_button(
            label="Descargar Mapa como HTML",
            data=f,
            file_name=output_file,
            mime="text/html"
        )
