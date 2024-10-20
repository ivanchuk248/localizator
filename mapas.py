import streamlit as st

# Título de la aplicación
st.title("GANACIA/PERDIDA NETA")


with open('ingreso.html', 'r', encoding='utf-8') as f:
    ingreso = f.read()

# Mostrar el mapa en la aplicación de Streamlit
st.components.v1.html(ingreso, height=600)

# Título de la aplicación
st.title("SECTORES")


with open('mapa_geolocalizado.html', 'r', encoding='utf-8') as f:
    mapa_geolocalizado = f.read()

# Mostrar el mapa en la aplicación de Streamlit
st.components.v1.html(mapa_geolocalizado, height=600)

st.title("DIRECTORIO COMPETENCIA")


with open('mapa_geolocalizado_buscador.html', 'r', encoding='utf-8') as f:
    mapa_geolocalizado_buscador = f.read()

# Mostrar el mapa en la aplicación de Streamlit
st.components.v1.html(mapa_geolocalizado_buscador, height=600)



