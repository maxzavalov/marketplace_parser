import telebot
from telebot import types
import time
import threading
from config import BOT_TOKEN


bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """Обработчик команд /start и /help"""
    welcome_text = """
🤖 <b>Добро пожаловать в Price Tracker Bot!</b>

Я помогу вам отслеживать цены на товары и уведомлю, когда цена упадет до нужного уровня!

<b>Доступные команды:</b>
/track - Начать отслеживание цены
/my_tracks - Мои отслеживаемые товары
/search - Быстрый поиск без отслеживания
/help - Показать эту справку

<b>Как отслеживать цены:</b>
1. Используйте /track
2. Выберите маркетплейс
3. Введите название товараgitad
4. Укажите целевую цену
5. Получайте уведомления!

🕐 <i>Проверка цен происходит каждые 30 минут</i>
    """

    bot.send_message(message.chat.id, welcome_text, parse_mode='HTML')


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