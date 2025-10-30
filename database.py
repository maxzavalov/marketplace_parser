import sqlite3
import json
from datetime import datetime
from models import TrackedProduct, PriceHistory


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