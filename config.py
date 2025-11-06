import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_TELEGRAM_BOT_TOKEN')

# Настройки планировщика
SCHEDULER_CONFIG = {
    'check_interval_minutes': 30,  # Интервал проверки цен
    'retry_delay_minutes': 5,      # Задержка при ошибке
    'max_workers': 3               # Максимальное количество потоков
}
