import telebot
from telebot import types
import time
import threading
from config import BOT_TOKEN
from parsers import WildberriesParser, OzonParser

bot = telebot.TeleBot(BOT_TOKEN)
# Словарь для хранения состояний пользователей
user_states = {}

wb_parser = WildberriesParser()
ozon_parser = OzonParser()

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


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    """Обработчик всех текстовых сообщений"""
    user_id = message.chat.id
    state = get_user_state(user_id)
    text = message.text.strip()

    # Обработка отмены
    if text == '❌ Отмена':
        _reset_user_state(user_id)
        bot.send_message(user_id, "❌ Действие отменено.", reply_markup=types.ReplyKeyboardRemove())
        return
    # Этап 1: Выбор маркетплейса
    if state.waiting_for_query and not state.selected_marketplace:
        if text in ['🟣 Wildberries', '🔍 Wildberries']:
            state.selected_marketplace = 'wildberries'
            marketplace_name = "Wildberries"
        elif text in ['🔵 Ozon', '🔍 Ozon']:
            state.selected_marketplace = 'ozon'
            marketplace_name = "Ozon"
        else:
            bot.send_message(user_id, "❌ Пожалуйста, выберите маркетплейс из кнопок.")
            return

        bot.send_message(
            user_id,
            f"🔍 <b>Поиск на {marketplace_name}</b>\nВведите название товара:",
            parse_mode='HTML',
            reply_markup=types.ReplyKeyboardRemove()
        )
        return

    # Этап 2: Ввод запроса для поиска
    if state.waiting_for_query and state.selected_marketplace and not state.current_query:
        state.current_query = text

        # Запускаем поиск товаров
        search_msg = bot.send_message(user_id, "🔍 <b>Ищем товары...</b>", parse_mode='HTML')

        thread = threading.Thread(
            target=_search_products,
            args=(user_id, text, state.selected_marketplace, search_msg.message_id)
        )
        thread.start()
        return



    # Обработка удаления отслеживания
    elif text.isdigit():
        _handle_delete_track(user_id, int(text))
    else:
        bot.send_message(user_id, "❓ Не понимаю команду. Используйте /help для справки.")

def _search_products(user_id, query, marketplace, message_id):
    """Поиск товаров в отдельном потоке"""
    try:
        bot.delete_message(user_id, message_id)

        status_msg = bot.send_message(user_id, f"🔍 <b>Ищем '{query}' на {marketplace}...</b>", parse_mode='HTML')

        # Выбираем парсер
        parser = wb_parser if marketplace == 'wildberries' else ozon_parser
        products = parser.parse_search(query, max_products=5)

        if not products:
            bot.edit_message_text(
                f"❌ По запросу '{query}' на {marketplace} ничего не найдено.",
                user_id,
                status_msg.message_id
            )
            _reset_user_state(user_id)
            return

        # Показываем найденные товары
        response = f"🔍 <b>Найдены товары по запросу '{query}':</b>\n\n"

        for i, product in enumerate(products, 1):
            response += f"<b>{i}. {product['name']}</b>\n"
            response += f"💰 <b>Цена:</b> {product['price']}\n"
            response += f"⭐ <b>Рейтинг:</b> {product['rating']}\n\n"

        markup = types.InlineKeyboardMarkup()
        for i in range(len(products)):
            markup.add(types.InlineKeyboardButton(f"Выбрать товар {i + 1}", callback_data=f"select_{i}"))

        bot.edit_message_text(
            response,
            user_id,
            status_msg.message_id,
            parse_mode='HTML',
            reply_markup=markup
        )

        # Сохраняем найденные товары во временное состояние
        state = get_user_state(user_id)
        state.search_results = products

    except Exception as e:
        bot.edit_message_text(
            f"❌ Ошибка при поиске: {e}",
            user_id,
            status_msg.message_id
        )
        _reset_user_state(user_id)


def _handle_delete_track(user_id, track_number):
    """Обработка удаления отслеживания"""
    pass


def _reset_user_state(user_id):
    """Сброс состояния пользователя"""
    if user_id in user_states:
        user_states[user_id] = UserState()


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
