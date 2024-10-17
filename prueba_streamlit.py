import streamlit as st
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt

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


# Función para recuperar los datos de la base de datos
def obtener_datos(conn):
    query = "SELECT * FROM locales;"
    df = pd.read_sql(query, conn)
    return df


# Título de la aplicación
st.title("Listado de Locales en Bogotá")

# Conectar a la base de datos
conn = conectar_db()

# Recuperar los datos
df_locales = obtener_datos(conn)

# Cerrar la conexión a la base de datos
conn.close()

# Mostrar datos en Streamlit
if df_locales.empty:
    st.write("No se encontraron locales.")
else:
    st.write(f"Total de locales encontrados: {len(df_locales)}")

    # Mostrar tabla con los locales
    st.dataframe(df_locales)

    # Agregar opción para filtrar los datos
    st.sidebar.header("Filtros")

    # Filtro por operación
    operaciones = df_locales['operacion'].unique()
    operacion_seleccionada = st.sidebar.selectbox("Seleccionar operación:", options=operaciones)

    # Filtrar DataFrame
    df_filtrado = df_locales[df_locales['operacion'] == operacion_seleccionada]

    if df_filtrado.empty:
        st.write("No se encontraron locales para la operación seleccionada.")
    else:
        st.write(f"Total de locales para '{operacion_seleccionada}': {len(df_filtrado)}")
        st.dataframe(df_filtrado)

        # Mostrar detalles de un local seleccionado
        local_seleccionado = st.sidebar.selectbox("Seleccionar local:", options=df_filtrado['enlace_detalle'].tolist())
        detalle_local = df_filtrado[df_filtrado['enlace_detalle'] == local_seleccionado].iloc[0]

        st.sidebar.subheader("Detalles del local")
        st.sidebar.write(f"Enlace: {detalle_local['enlace_detalle']}")
        st.sidebar.write(f"Precio: {detalle_local['precio']} {detalle_local['moneda']}")
        st.sidebar.write(f"Ubicación: {detalle_local['ubicacion']}")
        st.sidebar.write(f"Agencia: {detalle_local['agencia']}")
        st.sidebar.write(f"Descripción: {detalle_local['descripcion']}")

        # Gráfico de distribución de precios
        st.subheader("Distribución de Precios")
        df_filtrado['precio'] = pd.to_numeric(
            df_filtrado['precio'].str.replace(',', '').str.replace('COP', '').str.strip(), errors='coerce')
        st.write("Histograma de precios")
        plt.figure(figsize=(10, 5))
        plt.hist(df_filtrado['precio'].dropna(), bins=30, color='blue', alpha=0.7)
        plt.xlabel('Precio (COP)')
        plt.ylabel('Frecuencia')
        plt.title('Distribución de Precios de Locales')
        st.pyplot(plt)

        # Gráfico de locales por operación
        st.subheader("Cantidad de Locales por Operación")
        locales_por_operacion = df_locales['operacion'].value_counts()
        plt.figure(figsize=(10, 5))
        locales_por_operacion.plot(kind='bar', color='orange')
        plt.xlabel('Operación')
        plt.ylabel('Cantidad de Locales')
        plt.title('Cantidad de Locales por Operación')
        st.pyplot(plt)
