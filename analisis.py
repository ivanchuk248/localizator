# analisis.py

import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

def realizar_analisis(data):
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
