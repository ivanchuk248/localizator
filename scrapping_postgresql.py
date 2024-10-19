import requests
from lxml import html
from bs4 import BeautifulSoup
import psycopg2
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# Número máximo de páginas que deseas recorrer
max_pages = 60

# Datos de conexión a PostgreSQL
db_host = "brmifmitysqdshmrmblh-postgresql.services.clever-cloud.com"
db_name = "brmifmitysqdshmrmblh"
db_user = "uz5x38eqwuqxrodugfcb"
db_port = 50013
db_password = "SaTxVrCVimar29oRIFYTv3uYLaRf4B"

# Variable que determina si se eliminan los registros existentes
eliminar = True

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

# Crear tabla si no existe
def crear_tabla(conn):
    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS locales (
            
                id SERIAL PRIMARY KEY,
                titulo TEXT,
                enlace TEXT,
                precio VARCHAR(50),
                moneda VARCHAR(10),
                operacion VARCHAR(50),
                ubicacion TEXT,
                agencia TEXT,
                descripcion TEXT,
                imagen_URL TEXT,
                banos VARCHAR(10),
                area VARCHAR(20)
            )
        """)
        conn.commit()

# Eliminar registros de la tabla
def eliminar_registros(conn):
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM locales")
        conn.commit()

# Insertar datos en la tabla
def insertar_datos(conn, titulo, enlace, enlace_detalle, precio, moneda, operacion, ubicacion, agencia, descripcion, image_url, banos, area):
    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO locales (titulo, enlace, precio, moneda, operacion, ubicacion, agencia, descripcion, imagen_URL, banos, area)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (titulo, enlace, precio, moneda, operacion, ubicacion, agencia, descripcion, image_url, banos, area))
        conn.commit()

# Función para extraer la descripción de la página de detalles
def obtener_descripcion(detalle_url):
    response = requests.get(detalle_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        descripcion_div = soup.find('div', class_='description')
        if descripcion_div:
            descripcion = descripcion_div.find('div', id='description-text').text.strip()
            return descripcion
        else:
            return 'Descripción no disponible'
    else:
        return 'Error al cargar la página de detalles'


def obtener_meta_description(url: str) -> str:
    """Obtiene el contenido de la etiqueta <meta name="description"> de una página utilizando Selenium."""
    # Configurar opciones para Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Ejecutar en modo headless (sin ventana)

    # Inicializar el navegador
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

    try:
        driver.get(url)
        time.sleep(1)  # Esperar un momento para que la página cargue completamente

        # Buscar la etiqueta <meta name="description">
        meta_description = driver.find_element("xpath", "//meta[@name='description']")

        # Retornar el contenido de la etiqueta
        return meta_description.get_attribute("content")

    except Exception as e:
        print(f"Error al obtener la descripción: {e}")
        return 'Descripción no disponible'  # Retornar un mensaje de error

    finally:
        driver.quit()  # Cerrar el navegador


# Conectar a la base de datos
conn = conectar_db()
crear_tabla(conn)  # Crear la tabla si no existe









# Verificar si se deben eliminar los registros existentes
if eliminar:
    print("Eliminando registros existentes...")
    eliminar_registros(conn)

# Iterar sobre las páginas
for page in range(1, max_pages + 1):
    url = f"https://www.properati.com.co/s/bogota-d-c-colombia/local/arriendo/{page}"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        listings = soup.find_all('div', class_='listing listing-card')

        for idx, listing in enumerate(listings, start=1):
            #extraigo titulodel anuncio
            title_div = listing.find('div', class_='listing-card__title')
            title = title_div.text if title_div else 'N/A'

            link = listing['data-href'] if listing.has_attr('data-href') else 'N/A'
            price = listing['data-price'] if listing.has_attr('data-price') else 'N/A'
            currency = listing['data-currency'] if listing.has_attr('data-currency') else 'N/A'
            operation_type = listing['data-operation-type'] if listing.has_attr('data-operation-type') else 'N/A'
            location = listing['data-location'] if listing.has_attr('data-location') else 'N/A'
            agency_name = listing['data-nombreagencia'] if listing.has_attr('data-nombreagencia') else 'N/A'
            detail_link = listing.find('a', href=True)
            full_link = f"https://www.properati.com.co{detail_link['href']}" if detail_link else 'N/A'
            descripcion = obtener_meta_description("https://www.properati.com.co" + link)
            # Extraer la URL de la imagen
            # Extraer la URL de la imagen


            # Extraigo imagen
            swiper_container = listing.find('div', class_='swiper-container')
            img_tag = swiper_container.find('img', class_='swiper-no-swiping') if swiper_container else None
            image_url = img_tag['src'] if img_tag else 'N/A'

            info_bottom = listing.find('div', class_='listing-card__information-bottom')
            bathrooms = 'N/A'
            area = 'N/A'

            if info_bottom:
                # Busco el div que contiene los baños
                bathrooms_div = info_bottom.find('div', class_='card-icon card-icon__bathrooms')
                if bathrooms_div:
                    bathrooms_span = bathrooms_div.find_next_sibling('span')
                    bathrooms = bathrooms_span['content'] if bathrooms_span and bathrooms_span.has_attr(
                        'content') else 'N/A'

                # Busco el div que contiene el área
                area_div = info_bottom.find('div', class_='card-icon card-icon__area')
                if area_div:
                    area_span = area_div.find_next_sibling('span')
                    area = area_span.text.split()[0] if area_span else 'N/A'  # Solo el número

            # Insertar los datos en la base de datos
            insertar_datos(conn, title, "https://www.properati.com.co" + link,
                           full_link, price, currency, operation_type, location, agency_name,
                           descripcion, image_url, bathrooms, area)


            print(f"Página {page} - Anuncio {idx}")
            print(f"Título: {title} ")
            print(f"Enlace: https://www.properati.com.co{link}")
            print(f"Enlace del detalle: {full_link}")
            print(f"Precio: {price} {currency}")
            print(f"Operación: {operation_type}")
            print(f"Ubicación: {location}")
            print(f"Agencia: {agency_name}")
            print(f"Descripción: {descripcion}")
            print(f"Enlace de la imagen: {image_url}")
            print(f"Baños: {bathrooms}")
            print(f"Área: {area}")
            print("-----------")

    else:
        print(f"Error al realizar la solicitud en la página {page}.")

# Cerrar la conexión a la base de datos al final
conn.close()