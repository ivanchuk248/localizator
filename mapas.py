import streamlit as st

# Título de la aplicación
st.title("GANACIA/PERDIDA NETA")


with open('ingreso.html', 'r', encoding='utf-8') as f:
    ingreso = f.read()

# Mostrar el mapa en la aplicación de Streamlit
st.components.v1.html(ingreso, height=600)

# Título de la aplicación
st.title("GANACIA/PERDIDA NETA")


with open('ingreso.html', 'r', encoding='utf-8') as f:
    ingreso = f.read()

# Mostrar el mapa en la aplicación de Streamlit
st.components.v1.html(ingreso, height=600)



