import telebot
from telebot import types
import time
import threading
from config import BOT_TOKEN
from parsers import WildberriesParser, OzonParser

bot = telebot.TeleBot(BOT_TOKEN)
# Словарь для хранения состояний пользователей
user_states = {}


class UserState:
    """
    Класс описывает текущее состояние пользователя
    """
    def __init__(self):
        self.waiting_for_query = False
        self.waiting_for_target_price = False
        self.selected_marketplace = None
        self.current_query = None
        self.selected_product = None


def get_user_state(user_id):
    if user_id not in user_states:
        user_states[user_id] = UserState()
    return user_states[user_id]


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


@bot.message_handler(commands=['track'])
def start_tracking(message):
    """Начало процесса отслеживания"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_wb = types.KeyboardButton('🟣 Wildberries')
    btn_ozon = types.KeyboardButton('🔵 Ozon')
    btn_cancel = types.KeyboardButton('❌ Отмена')
    markup.add(btn_wb, btn_ozon, btn_cancel)

    bot.send_message(
        message.chat.id,
        "🎯 <b>Отслеживание цены</b>\nВыберите маркетплейс:",
        reply_markup=markup,
        parse_mode='HTML'
    )

    state = get_user_state(message.chat.id)
    state.waiting_for_query = True
    state.waiting_for_target_price = False

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
