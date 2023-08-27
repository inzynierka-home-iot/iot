import logging
import env
import telegram
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext
from paho.mqtt import client as mqtt_client

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

client = None
port = 1883
led_topic = 'home/led'
temp_topic = 'home/temp'
button_topic = 'home/button'
debug_topic = 'home/debug'
client_id = 'python-mqtt'
chat_id = env.TELEGRAM_USER_ID
temp = None
temp_subscribed = False

def connect_mqtt(broker) -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
            subscribe(client, [(temp_topic, 0), (button_topic, 0), (debug_topic, 0)])
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def publish_start(client, topic):
    msg = 'LED1-ON'
    result = client.publish(topic, msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic}")

def publish_stop(client, topic):
    msg = 'LED1-OFF'
    result = client.publish(topic, msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic}")

def subscribe(client, topics):
    bot = telegram.Bot(token=env.TELEGRAM_BOT_TOKEN)

    def on_message(client, userdata, msg):
        if msg.topic == temp_topic:
            global temp
            temp = msg.payload.decode().split('-')[1]
            print(f'Received message {msg.payload.decode()} from topic {msg.topic} with temp {temp}')
            if temp_subscribed:
                bot.send_message(chat_id=chat_id, text=f'Temperature is {temp}')
        elif msg.topic == button_topic:
            print(f'Received message {msg.payload.decode()} from topic {msg.topic}')
            bot.send_message(chat_id=chat_id, text='Button clicked')
        elif msg.topic == debug_topic:
            print(f'New device has been connected {msg.payload.decode()}')
            bot.send_message(chat_id=chat_id, text=f'New device has been connected {msg.payload.decode()}')

    client.subscribe(topics)
    client.on_message = on_message

def handle_message(update: Update, context: CallbackContext):
    global chat_id
    global temp_subscribed
    chat_id = update.effective_chat.id
    message_text = update.message.text

    if message_text == '/lightsOn':
        context.bot.send_message(chat_id=chat_id, text=f'Lights turned on! You are enlighted now!')
        publish_start(client, led_topic)
    elif message_text == '/lightsOff':
        context.bot.send_message(chat_id=chat_id, text=f'Lights turned off! Darkness is among us!')
        publish_stop(client, led_topic)
    elif message_text == '/getTemp':
        context.bot.send_message(chat_id=chat_id,  text=f'Temperature is {temp}')
    elif message_text == '/subscribeTemp':
        context.bot.send_message(chat_id=chat_id, text=f'Temperature subscribed!')
        temp_subscribed = True
    elif message_text == '/unsubscribeTemp':
        context.bot.send_message(chat_id=chat_id, text=f'Temperature unsubscribed!')
        temp_subscribed = False
    else:
        context.bot.send_message(chat_id=chat_id, text='Unknown command')

if __name__ == '__main__':
    updater = Updater(token=env.TELEGRAM_BOT_TOKEN)
    dispatcher = updater.dispatcher
    client = connect_mqtt(env.BROKER_IP)
    client.loop_start()

    dispatcher.add_handler(MessageHandler(Filters.command, handle_message))

    updater.start_polling()