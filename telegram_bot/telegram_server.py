import logging
import env
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, filters, MessageHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get the text of the user's message
    message_text = update.message.text
    print(f"Message: {message_text}")

    if message_text == "/lightsOn":
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=f"Lights turned on! You are enlighted now!")
    elif message_text == "/lightsOff":
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=f"Lights turned off! Darkness is among us!")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=f"Unknow command {message_text}")


if __name__ == '__main__':
    application = ApplicationBuilder().token(env.TELEGRAM_BOT_TOKEN).build()

    application.add_handler(MessageHandler(filters.COMMAND, handle_message))

    application.run_polling()
