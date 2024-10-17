import streamlit as st
import folium
from geopy.geocoders import Nominatim
import requests
import pandas as pd
from streamlit_folium import st_folium

# Título de la aplicación
st.title("Geocodificación y Mapa de Lugares de Interés")

# Crear un geocodificador con un user_agent único
geolocator = Nominatim(user_agent="mi_aplicacion_geocodificacion_v1.0")

# Inicializar session_state para almacenar datos del mapa y lugares de interés
if 'mapa' not in st.session_state:
    st.session_state.mapa = None
if 'lugares_interes' not in st.session_state:
    st.session_state.lugares_interes = []

# Entrada de dirección por parte del usuario
direccion = st.text_input("Introduce la dirección a geocodificar:", "venecia, tunjuelito")

# Botón para geocodificar
if st.button("Geocodificar"):
    # Limpiar la lista de lugares de interés
    st.session_state.lugares_interes.clear()

    # Obtener la ubicación
    ubicacion = geolocator.geocode(direccion)

    if ubicacion:
        # Coordenadas de la ubicación
        latitud = ubicacion.latitude
        longitud = ubicacion.longitude

        # Crear un nuevo mapa centrado en la ubicación
        st.session_state.mapa = folium.Map(location=[latitud, longitud], zoom_start=14)

        # Agregar un marcador en la ubicación
        folium.Marker(
            location=[latitud, longitud],
            popup=f"<strong>Ubicación: {direccion}</strong>",
            icon=folium.Icon(color='blue')
        ).add_to(st.session_state.mapa)

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

        if response.ok:  # Verificar si la respuesta es correcta
            data = response.json()

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
                            popup=(f"<strong>{name}</strong><br>"
                                   f"<em>Tipo:</em> {amenity}<br>"
                                   f"<em>Dirección:</em> {address}<br>"
                                   f"<em>Sitio Web:</em> {website}<br>"
                                   f"<em>Horario:</em> {opening_hours}"),
                            icon=folium.Icon(color='green')
                        ).add_to(st.session_state.mapa)

                        # Agregar a la lista de lugares de interés
                        st.session_state.lugares_interes.append({
                            'Lugar': name,
                            'Tipología': amenity,
                            'Dirección': address,
                            'Sitio Web': website,
                            'Horario': opening_hours
                        })

            # Crear un DataFrame con los lugares de interés
            df_lugares = pd.DataFrame(st.session_state.lugares_interes)

            # Mostrar el mapa en Streamlit
            st.subheader("Mapa de la Ubicación")
            st_folium(st.session_state.mapa, width=700, height=500)

            # Mostrar el DataFrame
            st.subheader("Lugares de Interés Encontrados")
            if not df_lugares.empty:
                st.dataframe(df_lugares)
            else:
                st.warning("No se encontraron lugares de interés en esta área.")
        else:
            st.error("Error al consultar la API de Overpass. Intenta de nuevo más tarde.")
    else:
        st.error("La dirección no se pudo geocodificar.")

# Mostrar el mapa y la tabla si ya se han creado
if st.session_state.mapa is not None:
    st.subheader("Mapa de la Ubicación")
    st_folium(st.session_state.mapa, width=700, height=500)

if st.session_state.lugares_interes:
    df_lugares = pd.DataFrame(st.session_state.lugares_interes)
    st.subheader("Lugares de Interés Encontrados")
    st.dataframe(df_lugares)
