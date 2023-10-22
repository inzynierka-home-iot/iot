import logging
import env
import telegram
import time
import threading
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
            logging.log(logging.INFO, 'Connected to MQTT Broker!')
            subscribe(client, [('home-1-out/#', 0), ('home-1-in/#', 0)])
        else:
            logging.log(logging.ERROR, f'Failed to connect, return code {rc}\n')

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
        logging.log(logging.INFO, f'Send `{msg}` to topic `{topic}`')
    else:
        logging.log(logging.ERROR, f'Failed to send message to topic `{topic}`')

def publish_message(client, home_id, node_id, device_id, set, action_params):
    action_name = action_params.split('=')[0]
    action_value = action_params.split('=')[1]
    topic = f'{home_id}-in/{node_id}/{device_id}/{"1" if set else "2"}/0/{ActionType[action_name].value[0]}'
    result = client.publish(topic, action_value)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        logging.log(logging.INFO, f'Send `{action_value}` to topic `{topic}`')
        return True
    else:
        logging.log(logging.ERROR, f'Failed to send message to topic `{topic}`')
        return False


def subscribe(client, topics):
    bot = telegram.Bot(token=env.TELEGRAM_BOT_TOKEN)

    def on_message(client, userdata, msg):
        global connected_devices
        location, node_id, device_id, command, ack, type_id = msg.topic.split('/')
        location = location.split('-out')[0]
        device = Device(location, node_id, device_id, list(DeviceType)[int(type_id)].name, msg.payload.decode())
        if command == '0':
            if device in connected_devices:
                index = connected_devices.index(device)
                connected_devices[index] = device
            else:
                connected_devices.append(device)
                bot.send_message(chat_id=chat_id, text=f'{{"req": "/{location}/{node_id}/{device_id}/connected/", "res": {{"device": {device}}}}}')
        elif command == '1':
            if device in connected_devices:
                index = connected_devices.index(device)
                connected_devices[index].update_value(list(ActionType)[int(type_id)].name, msg.payload.decode())
                if connected_devices[index].values[list(ActionType)[int(type_id)].name][1]:
                    bot.send_message(chat_id=chat_id, text=f'{connected_devices[index].get_value(list(ActionType)[int(type_id)].name)}')
        elif command == '3':
            if type_id == '22':
                node_devices = [d for d in connected_devices if d.location == location and d.node_id == node_id]
                for node_device in node_devices:
                    node_device.update_last_seen()

    client.subscribe(topics)
    client.on_message = on_message


def handle_message(update: Update, context: CallbackContext):
    global chat_id
    chat_id = update.effective_chat.id
    message_text = update.message.text
    logging.log(logging.INFO, f'Received from app: {message_text}')

    if message_text.count('/') < 5:
        context.bot.send_message(chat_id=chat_id, text=f'{{"req": "{message_text}", "res": {{"status": false}}}}')
        return
    _, home_id, node_id, device_id, action, params = message_text.split('/')

    if action == 'status':
        requests = params.split('?')[1:]
        device = Device(home_id, node_id, device_id, None, None)

        if home_id != '*' and node_id != '*' and device_id != '*' and device in connected_devices:
            index = connected_devices.index(device)
            if len(requests) == 0:
                response = connected_devices[index].get_value()
            else:
                response = connected_devices[index].get_value(requests)
            context.bot.send_message(chat_id=chat_id, text=f'{{"req": "{message_text}", "res": {response}}}')
        else:
            context.bot.send_message(chat_id=chat_id, text=f'{{"req": "{message_text}", "res": {{"status": false}}}}')
    elif action == 'statusAll':
        if params.strip():
            value_type = params.split('?')[1]
            device = Device(home_id, node_id, device_id, None, None)

            if home_id != '*' and node_id != '*' and device_id != '*' and device in connected_devices:
                index = connected_devices.index(device)
                response = connected_devices[index].get_historical_values(value_type)
                context.bot.send_message(chat_id=chat_id, text=f'{{"req": "{message_text}", "res": {response}}}')
            else:
                context.bot.send_message(chat_id=chat_id, text=f'{{"req": "{message_text}", "res": {{"status": false}}}}')
        else:
            context.bot.send_message(chat_id=chat_id, text=f'{{"req": "{message_text}", "res": {{"status": false}}}}')
    elif action == 'set':
        if params.strip():
            result = True
            action_param = params.split('?')[1]
            action_type = action_param.split('=')[0]
            possible_devices = [device for device in connected_devices if action_type in device.values]
            if home_id == '*':
                for device in possible_devices:
                    result = result and publish_message(client, device.location, device.node_id, device.device_id, True, action_param)
            else:
                if node_id == '*':
                    for device in [device for device in possible_devices if device.location == home_id]:
                        result = result and publish_message(client, device.location, device.node_id, device.device_id, True, action_param)
                else:
                    if device_id == '*':
                        for device in [device for device in possible_devices if device.location == home_id and device.node_id == node_id]:
                            result = result and publish_message(client, device.location, device.node_id, device.device_id, True, action_param)
                    else:
                        result = publish_message(client, home_id, node_id, device_id, True, action_param)

            if result:
                context.bot.send_message(chat_id=chat_id, text=f'{{"req": "{message_text}", "res": {{"status": true}}}}')
            else:
                context.bot.send_message(chat_id=chat_id, text=f'{{"req": "{message_text}", "res": {{"status": false}}}}')
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
                    device = Device(home_id, node_id, device_id, None, None)
                    if device in connected_devices:
                        index = connected_devices.index(Device(home_id, node_id, device_id, None, None))
                        context.bot.send_message(chat_id=chat_id, text=f'{{"req": "{message_text}", "res": {connected_devices[index]}}}')
                    else:
                        context.bot.send_message(chat_id=chat_id, text=f'{{"req": "{message_text}", "res": {{"status": false}}}}')
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

def check_connected():
    bot = telegram.Bot(token=env.TELEGRAM_BOT_TOKEN)

    while True:
        for device in connected_devices:
            publish_raw(client, f'{device.location}-in/{device.node_id}/{device.device_id}/3/0/18:0')
        for device in connected_devices:
            if time.time() - device.last_seen > 120:
                connected_devices.remove(device)
                bot.send_message(chat_id=chat_id, text=f'{{"req": "/{device.location}/{device.node_id}/{device.device_id}/disconnected/", "res": {{"device": {device}}}}}')
        time.sleep(30)



if __name__ == '__main__':
    updater = Updater(token=env.TELEGRAM_BOT_TOKEN)
    dispatcher = updater.dispatcher
    client = connect_mqtt(env.BROKER_IP)
    client.loop_start()

    dispatcher.add_handler(MessageHandler(Filters.text, handle_message))
    t = threading.Thread(target=check_connected)
    t.start()

    updater.start_polling()
