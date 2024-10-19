# funciones.py

import pandas as pd
import folium

def cargar_datos():
    # Reemplaza con el código para cargar tus datos
    # Ejemplo: data = pd.read_csv('tus_datos.csv')
    data = pd.DataFrame({
        'ubicacion': ['Ubicación 1', 'Ubicación 2'],
        'precio': [100, 200],
        'operacion': ['Alquilar', 'Vender'],
        'agencia': ['Agencia 1', 'Agencia 2'],
        'imagen_url': ['url1.jpg', 'url2.jpg'],
        'enlace': ['enlace1', 'enlace2']
    })
    return data

def despliegue_mapa(ubicacion):
    # Función para desplegar el mapa
    mapa = folium.Map(location=[4.61, -74.08], zoom_start=12)  # Coordenadas de Bogotá
    folium.Marker(location=[4.61, -74.08], popup=ubicacion).add_to(mapa)
    return mapa
