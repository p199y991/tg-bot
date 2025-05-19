from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ChatMemberHandler,
    ContextTypes,
)
from dotenv import load_dotenv
import os

load_dotenv()  # Загружает переменные из .env

TOKEN = os.getenv("BOT_TOKEN")


# Обработчик события добавления бота в канал
async def added_to_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_chat_member = update.chat_member.new_chat_member
    if new_chat_member.status == "administrator":
        await context.bot.send_message(
            chat_id=update.chat_member.chat.id,
            text="Бот подключился к каналу и готов принимать сообщения.",
        )


# Функция для показа кнопки "Отправить текст"
async def show_send_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    channel_id = update.channel_post.chat.id
    keyboard = [
        [InlineKeyboardButton("Отправить текст", callback_data=f"send_{channel_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.channel_post.reply_text(
        "Хотите опубликовать сообщение?", reply_markup=reply_markup
    )


# Обработчик нажатия кнопки
async def handle_button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    channel_id = int(query.data.split("_")[1])  # Извлекаем ID канала из callback_data
    await query.edit_message_text(
        text=f"Введите сообщение для канала {query.message.chat.title}:"
    )


# Обработчик сообщений в приватном чате с ботом
async def process_private_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    sender_username = (
        update.message.from_user.username or update.message.from_user.first_name
    )
    channel_id = int(
        update.message.text.split(":")[0].strip()
    )  # Извлекаем ID канала из сообщения

    # Форматируем сообщение с указанием отправителя
    formatted_message = f"{sender_username}: {user_message}"
    try:
        # Отправляем сообщение в канал
        await context.bot.send_message(chat_id=channel_id, text=formatted_message)
        await update.message.reply_text("Ваше сообщение опубликовано в канале.")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {str(e)}")


# Главный цикл работы бота
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    # Добавляем обработчики
    app.add_handler(
        ChatMemberHandler(
            added_to_channel, chat_member_types=(ChatMemberHandler.CHAT_MEMBER)
        )
    )  # Обработчик добавления в канал
    app.add_handler(
        CommandHandler("start", show_send_button)
    )  # Показ кнопки при команде /start
    app.add_handler(
        CallbackQueryHandler(handle_button_click)
    )  # Обработка нажатия кнопки
    app.add_handler(
        MessageHandler(
            filters.ChatType.PRIVATE & ~filters.COMMAND, process_private_message
        )
    )

    # Начинаем приём сообщений
    app.run_polling()
