import logging
import env
import telegram
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext
from paho.mqtt import client as mqtt_client
from device import Device
from device_types import DeviceType
from action_types import ActionType
from connected_devices import connected_devices

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

client = None
port = 1883
client_id = 'python-mqtt'
chat_id = env.TELEGRAM_USER_ID
connected_devices = connected_devices


def connect_mqtt(broker) -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print('Connected to MQTT Broker!')
            subscribe(client, [('home-1-out/#', 0), ('home-1-in/#', 0)])
        else:
            print('Failed to connect, return code %d\n', rc)

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def publish_raw(client, msg):
    home_id_in, node_id, device_id, command, ack, t_msg = msg.split('/')
    t, payload = t_msg.split(':')
    topic = f'{home_id_in}/{node_id}/{device_id}/{command}/{ack}/{t}'
    result = client.publish(topic, payload)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f'Send `{msg}` to topic `{topic}`')
    else:
        print(f'Failed to send message to topic `{topic}`')

def publish_message(client, home_id, node_id, device_id, set, params):
    actions = params.split('?')[1:]
    for action in actions:
        action_name = action.split('=')[0]
        action_value = action.split('=')[1]
        topic = f'{home_id}-in/{node_id}/{device_id}/{"1" if set else "2"}/0/{ActionType[action_name].value[0]}'
        result = client.publish(topic, action_value)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            print(f'Send `{action_value}` to topic `{topic}`')
            return True
        else:
            print(f'Failed to send message to topic `{topic}`')
            return False


def subscribe(client, topics):
    bot = telegram.Bot(token=env.TELEGRAM_BOT_TOKEN)

    def on_message(client, userdata, msg):
        global connected_devices
        home, node, device, command, ack, t = msg.topic.split('/')
        home = home.split('-out')[0]
        device = Device(home, node, device, list(DeviceType)[int(t)].name, msg.payload.decode())
        if command == '0':
            if device in connected_devices:
                index = connected_devices.index(device)
                connected_devices[index] = device
            else:
                connected_devices.append(device)
        elif command == '1':
            if device in connected_devices:
                index = connected_devices.index(device)
                connected_devices[index].update_value(list(ActionType)[int(t)].name, msg.payload.decode())
                if connected_devices[index].values[list(ActionType)[int(t)].name][1]:
                    bot.send_message(chat_id=chat_id, text=f'{connected_devices[index].get_value(list(ActionType)[int(t)].name)}')

    client.subscribe(topics)
    client.on_message = on_message


def handle_message(update: Update, context: CallbackContext):
    global chat_id
    chat_id = update.effective_chat.id
    message_text = update.message.text
    logging.log(logging.INFO, f'Received from app: {message_text}')

    _, home_id, node_id, device_id, action, params = message_text.split('/')

    if action == 'status':
        response = f'{{ device: "{home_id}/{node_id}/{device_id}"'
        requests = params.split('?')[1:]
        device = Device(home_id, node_id, device_id, None, None)
        index = connected_devices.index(device)

        if len(requests) == 0:
            response += connected_devices[index].get_value()
        else:
            for request in requests:
                response += connected_devices[index].get_value(request)

        response += ' }'

        context.bot.send_message(chat_id=chat_id, text=response)
    elif action == 'set':
        result = publish_message(client, home_id, node_id, device_id, True, params)
        if result:
            context.bot.send_message(chat_id=chat_id, text=f'{{"req": "{message_text}", "res": {{"status": true}}}}')
        else:
            context.bot.send_message(chat_id=chat_id, text=f'{{"req": "{message_text}", "res": {{"status": false}}}}')
    elif action == 'get':
        if home_id == '*':
            context.bot.send_message(chat_id=chat_id, text=f'{{"req": "{message_text}", "res": {connected_devices}}}')
        else:
            if node_id == '*':
                context.bot.send_message(chat_id=chat_id, text=f'{{"req": "{message_text}", "res": {[device for device in connected_devices if device.location == home_id]}}}')
            else:
                if device_id == '*':
                    context.bot.send_message(chat_id=chat_id, text=f'{{"req": "{message_text}", "res": {[device for device in connected_devices if device.location == home_id and device.node_id == node_id]}}}')
                else:
                    index = connected_devices.index(Device(home_id, node_id, device_id, None, None))
                    context.bot.send_message(chat_id=chat_id, text=f'{{"req": "{message_text}", "res": {connected_devices[index]}}}')
    elif action == 'subscribe':
        requests = params.split('?')[1:]
        if len(requests) == 0:
            connected_devices[f'{home_id}/{node_id}/{device_id}'].subscribe()
        else:
            for request in requests:
                connected_devices[f'{home_id}/{node_id}/{device_id}'].subscribe(request)
    elif action == 'unsubscribe':
        requests = params.split('?')[1:]
        if len(requests) == 0:
            connected_devices[f'{home_id}/{node_id}/{device_id}'].unsubscribe()
        else:
            for request in requests:
                connected_devices[f'{home_id}/{node_id}/{device_id}'].unsubscribe(request)
    elif action == 'raw':
        publish_raw(client, message_text)
    else:
        context.bot.send_message(chat_id=chat_id, text='Unknown command')


if __name__ == '__main__':
    updater = Updater(token=env.TELEGRAM_BOT_TOKEN)
    dispatcher = updater.dispatcher
    client = connect_mqtt(env.BROKER_IP)
    client.loop_start()

    dispatcher.add_handler(MessageHandler(Filters.text, handle_message))

    updater.start_polling()
