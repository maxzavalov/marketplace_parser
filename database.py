import sqlite3
from datetime import datetime
from models import TrackedProduct, PriceHistory
from typing import List

class Database:
    def __init__(self, db_path='price_tracker.db'):
        self.db_path = db_path
    def init_database(self):
        """Инициализация таблиц в базе данных"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Таблица отслеживаемых товаров
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tracked_products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    search_query TEXT NOT NULL,
                    marketplace TEXT NOT NULL,
                    target_price REAL NOT NULL,
                    current_price REAL,
                    product_url TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TEXT NOT NULL,
                    last_checked TEXT NOT NULL
                )
            ''')

            # Таблица истории цен
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    price REAL NOT NULL,
                    checked_at TEXT NOT NULL,
                    FOREIGN KEY (product_id) REFERENCES tracked_products (id)
                )
            ''')

            conn.commit()

    def add_tracked_product(self, product: TrackedProduct) -> int:
        """Добавление товара для отслеживания"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO tracked_products 
                (user_id, name, search_query, marketplace, target_price, current_price, product_url, is_active, created_at, last_checked)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                product.user_id, product.name, product.search_query, product.marketplace,
                product.target_price, product.current_price, product.product_url,
                product.is_active, product.created_at, product.last_checked
            ))
            product_id = cursor.lastrowid
            conn.commit()
            return product_id

    def get_user_tracked_products(self, user_id: int) -> List[TrackedProduct]:
        """Получение всех отслеживаемых товаров пользователя"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM tracked_products 
                WHERE user_id = ? AND is_active = TRUE 
                ORDER BY created_at DESC
            ''', (user_id,))

            products = []
            for row in cursor.fetchall():
                products.append(TrackedProduct(
                    id=row[0], user_id=row[1], name=row[2], search_query=row[3],
                    marketplace=row[4], target_price=row[5], current_price=row[6],
                    product_url=row[7], is_active=bool(row[8]), created_at=row[9],
                    last_checked=row[10]
                ))
            return products

    def get_active_tracked_products(self) -> List[TrackedProduct]:
        """Получение всех активных отслеживаемых товаров"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM tracked_products 
                WHERE is_active = TRUE 
                ORDER BY last_checked ASC
            ''')

            products = []
            for row in cursor.fetchall():
                products.append(TrackedProduct(
                    id=row[0], user_id=row[1], name=row[2], search_query=row[3],
                    marketplace=row[4], target_price=row[5], current_price=row[6],
                    product_url=row[7], is_active=bool(row[8]), created_at=row[9],
                    last_checked=row[10]
                ))
            return products

    def update_product_price(self, product_id: int, new_price: float):
        """Обновление текущей цены товара"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            current_time = datetime.now().isoformat()

            cursor.execute('''
                UPDATE tracked_products 
                SET current_price = ?, last_checked = ?
                WHERE id = ?
            ''', (new_price, current_time, product_id))

            # Добавляем запись в историю цен
            cursor.execute('''
                INSERT INTO price_history (product_id, price, checked_at)
                VALUES (?, ?, ?)
            ''', (product_id, new_price, current_time))

            conn.commit()

    def get_price_history(self, product_id: int, limit: int = 10) -> List[PriceHistory]:
        """Получение истории цен для товара"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM price_history 
                WHERE product_id = ? 
                ORDER BY checked_at DESC 
                LIMIT ?
            ''', (product_id, limit))

            history = []
            for row in cursor.fetchall():
                history.append(PriceHistory(
                    id=row[0], product_id=row[1], price=row[2], checked_at=row[3]
                ))
            return history

    def delete_tracked_product(self, product_id: int, user_id: int) -> bool:
        """Удаление отслеживаемого товара"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM tracked_products 
                WHERE id = ? AND user_id = ?
            ''', (product_id, user_id))

            deleted = cursor.rowcount > 0
            conn.commit()
            return deleted

    def deactivate_product(self, product_id: int, user_id: int) -> bool:
        """Деактивация отслеживания товара"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE tracked_products 
                SET is_active = FALSE 
                WHERE id = ? AND user_id = ?
            ''', (product_id, user_id))

            updated = cursor.rowcount > 0
            conn.commit()
            return updated