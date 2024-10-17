import streamlit as st
import folium
from geopy.geocoders import Nominatim
import requests
import pandas as pd
from streamlit_folium import st_folium

# Título de la aplicación
st.title("Mapa de Venecia, Tunjuelito y lugares de interés")

# Crear un geocodificador con un user_agent único
geolocator = Nominatim(user_agent="mi_aplicacion_geocodificacion_v1.0")

# Dirección a geocodificar
direccion = "parque de los hippies, chapinero"

# Obtener la ubicación
ubicacion = geolocator.geocode(direccion)

if ubicacion:
    # Coordenadas de la ubicación
    latitud = ubicacion.latitude
    longitud = ubicacion.longitude

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
    data = response.json()

    # Crear una lista para almacenar los lugares y sus datos
    lugares_interes = []

    # Agregar lugares de interés al mapa y a la lista
    for element in data['elements']:
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
