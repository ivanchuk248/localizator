import requests
from bs4 import BeautifulSoup

for page in range(1, 5 + 1):
    url = f"https://www.properati.com.co/s/bogota-d-c-colombia/local/arriendo/{page}"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        listings = soup.find_all('div', class_='listing listing-card')

        for idx, listing in enumerate(listings, start=1):
            # Extraigo título del anuncio
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

            # Extraigo imagen
            swiper_container = listing.find('div', class_='swiper-container')
            img_tag = swiper_container.find('img', class_='swiper-no-swiping') if swiper_container else None
            img_link = img_tag['src'] if img_tag else 'N/A'

            # Extraigo baños y metros cuadrados
            info_bottom = listing.find('div', class_='listing-card__information-bottom')
            bathrooms = 'N/A'
            area = 'N/A'

            if info_bottom:
                # Busco el div que contiene los baños
                bathrooms_div = info_bottom.find('div', class_='card-icon card-icon__bathrooms')
                if bathrooms_div:
                    bathrooms_span = bathrooms_div.find_next_sibling('span')
                    bathrooms = bathrooms_span['content'] if bathrooms_span and bathrooms_span.has_attr('content') else 'N/A'

                # Busco el div que contiene el área
                area_div = info_bottom.find('div', class_='card-icon card-icon__area')
                if area_div:
                    area_span = area_div.find_next_sibling('span')
                    area = area_span.text.split()[0] if area_span else 'N/A'  # Solo el número

            print(f"Página {page} - Anuncio {idx}")
            print(f"Título: {title}")
            print(f"Enlace: https://www.properati.com.co{link}")
            print(f"Enlace del detalle: {full_link}")
            print(f"Precio: {price} {currency}")
            print(f"Operación: {operation_type}")
            print(f"Ubicación: {location}")
            print(f"Agencia: {agency_name}")
            print(f"Enlace de la imagen: {img_link}")
            print(f"Baños: {bathrooms}")
            print(f"Área: {area}")
