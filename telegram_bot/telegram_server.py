import logging
import env
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, filters, MessageHandler
import mqtt_handler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
client = mqtt_handler.connect_mqtt(env.BROKER_IP)
led_topic = 'home/led'
temp_topic = 'home/temp'
button_topic = 'home/button'
debug_topic = 'home/debug'
chat_id = None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get the text of the user's message
    message_text = update.message.text
    print(f'Message: {message_text}')
    global chat_id
    chat_id = update.effective_chat.id

    if message_text == '/lightsOn':
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=f'Lights turned on! You are enlighted now!')
        mqtt_handler.publish_start(client, led_topic)
    elif message_text == '/lightsOff':
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=f'Lights turned off! Darkness is among us!')
        mqtt_handler.publish_stop(client, led_topic)
    elif message_text == '/getTemp':
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=f'Temperature is {mqtt_handler.get_temp()}')
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=f'Unknown command {message_text}')


if __name__ == '__main__':
    mqtt_handler.run(client)

    application = ApplicationBuilder().token(env.TELEGRAM_BOT_TOKEN).build()

    application.add_handler(MessageHandler(filters.COMMAND, handle_message))

    application.run_polling()
