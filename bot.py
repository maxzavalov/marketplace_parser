import telebot
from telebot import types
import time
import threading
from config import BOT_TOKEN


bot = telebot.TeleBot(BOT_TOKEN)



def main():
    """Основная функция запуска бота"""
    print("🤖 Price Tracker Bot запущен...")

    try:
        bot.polling(none_stop=True, interval=0)
    except Exception as e:
        print(f"❌ Ошибка при запуске бота: {e}")
        time.sleep(5)
        main()  # Перезапуск при ошибке


if __name__ == "__main__":
    main()