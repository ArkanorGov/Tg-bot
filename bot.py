import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import (InlineKeyboardMarkup, 
                          InlineKeyboardButton, 
                          ReplyKeyboardRemove)
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# Настройка логов
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота
storage = MemoryStorage()
bot = Bot(token=os.getenv('8044256507:AAH4TbMzkk-hx5UXUGwAuneTImikoDpFrbs'))
dp = Dispatcher(bot, storage=storage)

# Данные платежей
PAYMENT_DATA = {
    "card": {
        "text": """
💳 <b>Банковские реквизиты:</b>
Тинькофф: <code>2200 7017 8221 7225</code>

📌 <b>Обязательно укажите комментарий:</b>
<code>G{user_id}</code>""",
        "confirmation": "скриншот перевода"
    },
    "crypto": {
        "text": """
₿ <b>Криптоплатеж (USDT-TRC20):</b>
<code>TAbcde12345...</code>

📌 <b>Обязательно укажите в комментарии:</b>
<code>G{user_id}</code>""",
        "confirmation": "хеш транзакции (TxID)"
    }
}

# Команда /start
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("💵 Купить доступ", callback_data="init_payment"))
    
    await message.answer(
        "🏰 <b>Добро пожаловать в Первую мире Виртуальную страну!</b>\n\n"
        "Для получения доступа необходимо оплатить взнос 500₽.",
        reply_markup=keyboard,
        parse_mode='HTML'
    )

# Инициализация оплаты
@dp.callback_query_handler(text="init_payment")
async def select_payment(call: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("💳 Карта", callback_data="method_card"),
        InlineKeyboardButton("₿ Крипта", callback_data="method_crypto"),
        InlineKeyboardButton("❌ Отмена", callback_data="cancel")
    )
    
    await call.message.edit_text(
        "🔹 <b>Выберите способ оплаты:</b>",
        reply_markup=keyboard,
        parse_mode='HTML'
    )

# Отправка реквизитов
@dp.callback_query_handler(lambda c: c.data.startswith('method_'))
async def send_payment_details(call: types.CallbackQuery):
    method = call.data.split('_')[1]  # card или crypto
    user_id = call.from_user.id
    
    text = PAYMENT_DATA[method]["text"].format(user_id=user_id)
    confirm_type = PAYMENT_DATA[method]["confirmation"]
    
    await call.message.edit_text(
        f"{text}\n\n"
        f"После оплаты пришлите {confirm_type} этим сообщением.",
        parse_mode='HTML'
    )

# Обработка скриншотов/хешей
@dp.message_handler(content_types=['photo', 'text'])
async def handle_confirmation(message: types.Message):
    admin_id = int(os.getenv('7377016932'))
    
    if message.photo:
        # Для банковских переводов
        await bot.send_photo(
            admin_id,
            message.photo[-1].file_id,
            caption=f"🆕 Скриншот оплаты от @{message.from_user.username}\nID: {message.from_user.id}"
        )
        await message.reply(
            "✅ Скриншот получен! Доступ будет активирован в течение 24 часов.",
            reply_markup=ReplyKeyboardRemove()
        )
    
    elif message.text and (message.text.startswith('0x') or len(message.text) == 64):
        # Для криптоплатежей
        await bot.send_message(
            admin_id,
            f"🆔 Новая транзакция:\n"
            f"От: @{message.from_user.username}\n"
            f"ID: {message.from_user.id}\n"
            f"Хеш: <code>{message.text}</code>",
            parse_mode='HTML'
        )
        await message.reply(
            "✅ Хеш транзакции принят! Доступ будет активирован после подтверждения.",
            reply_markup=ReplyKeyboardRemove()
        )

# Запуск бота
if __name__ == '__main__':
    logger.info("Бот запущен")
    executor.start_polling(dp, skip_updates=True)
