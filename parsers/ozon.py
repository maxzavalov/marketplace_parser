import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import time
import re


class OzonParser:
    def __init__(self):
        self.base_url = "https://www.ozon.ru"
        self.search_url = "https://www.ozon.ru/search"
        self.ua = UserAgent()

    def get_headers(self):
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        }

    def parse_search(self, query, max_products=5):
        """
        Парсит результаты поиска Ozon
        """
        try:
            params = {
                'text': query,
                'from_global': 'true'
            }

            response = requests.get(
                self.search_url,
                params=params,
                headers=self.get_headers(),
                timeout=10
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'lxml')
            products = []

            # Ищем карточки товаров Ozon
            product_cards = soup.find_all('div', {'class': re.compile('tile-root')})

            for card in product_cards[:max_products]:
                product_data = self._parse_product_card(card)
                if product_data:
                    products.append(product_data)

                time.sleep(0.1)

            return products

        except Exception as e:
            print(f"Ошибка при парсинге Ozon: {e}")
            return []

    def _parse_product_card(self, card):
        """
        Парсит отдельную карточку товара Ozon
        """
        try:
            # Название товара
            name_elem = card.find('a', {'class': re.compile('tile-hover-target')})
            name = name_elem.get_text(strip=True) if name_elem else 'Название не найдено'

            # Цена
            price_elem = card.find('span', {'class': re.compile('price')})
            price = self._clean_price(price_elem.get_text(strip=True)) if price_elem else 'Цена не найдена'

            # Ссылка на товар
            link_elem = card.find('a', {'class': re.compile('tile-hover-target')})
            link = self.base_url + link_elem['href'] if link_elem and link_elem.get('href') else None

            # Рейтинг
            rating_elem = card.find('span', {'class': re.compile('rating')})
            rating = rating_elem.get_text(strip=True) if rating_elem else 'Нет оценок'

            return {
                'name': name,
                'price': price,
                'rating': rating,
                'reviews': 'N/A',
                'link': link,
                'marketplace': 'Ozon'
            }

        except Exception as e:
            print(f"Ошибка при парсинге карточки товара Ozon: {e}")
            return None

    def _clean_price(self, price_text):
        """
        Очищает цену от лишних символов для Ozon
        """
        # Удаляем валюту и лишние пробелы
        cleaned = re.sub(r'[^\d\s]', '', price_text).strip()
        cleaned = re.sub(r'\s+', '', cleaned)  # Удаляем пробелы между цифрами
        return f"{cleaned} руб." if cleaned else 'Цена не указана'