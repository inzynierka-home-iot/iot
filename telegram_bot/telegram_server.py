import logging
import env
import telegram
import time
import json
import threading
import subprocess
import atexit
import signal
import connected_devices
import sys
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext
from paho.mqtt import client as mqtt_client
from device import Device
from device_types import DeviceType
from action_types import ActionType
from scheduler import generate_new_schedule, generate_readable_scheduler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

client = None
port = 1883
client_id = 'python-mqtt'
chat_id = None
connected_devices = connected_devices.connected_devices
location = env.LOCATION


def connect_mqtt(broker) -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            logging.log(logging.INFO, 'Connected to MQTT Broker!')
            subscribe(client, [('nodeRed/#', 0), (f'{location}-out/#', 0)])
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
        # logging.log(logging.INFO, f'Send `{msg}` to topic `{topic}`')
        pass
    else:
        logging.log(logging.ERROR, f'Failed to send message to topic `{topic}`')


def publish_to_nodeRED(topic, msg):
    result = client.publish("nodeRED/" + topic, msg)
    status = result[0]
    if status == 0:
        logging.log(logging.INFO, f'Send `{msg}` to topic nodeRED {topic}')
        return True
    else:
        logging.log(logging.ERROR, f'Failed to send message to topic nodeRED `{topic}`')
        return False


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
        if msg.topic.startswith("nodeRed"):
            msg_payload = msg.topic[7:]
            handle_message(None, None, msg_payload)
            return

        location, node_id, device_id, command, ack, type_id = msg.topic.split('/')
        location = location.split('-out')[0]
        device = Device(location, node_id, device_id, '', '')
        if command == '0':
            device = Device(location, node_id, device_id, list(DeviceType)[int(type_id)].name, msg.payload.decode())
            if device in connected_devices:
                index = connected_devices.index(device)
                connected_devices[index].update_info(location, node_id, device_id, list(DeviceType)[int(type_id)].name, msg.payload.decode())
            else:
                connected_devices.append(device)
                if chat_id:
                    bot.send_message(chat_id=chat_id,
                                 text=f'{{"req": "/{location}/{node_id}/{device_id}/connected/", "res": {{"device": {device}}}}}')
        elif command == '1':
            if device in connected_devices:
                index = connected_devices.index(device)
                connected_devices[index].update_value(list(ActionType)[int(type_id)].name, msg.payload.decode())
                if connected_devices[index].values[list(ActionType)[int(type_id)].name][1]:
                    if chat_id:
                        bot.send_message(chat_id=chat_id,
                                     text=f'{connected_devices[index].get_dump_values(list(ActionType)[int(type_id)].name)}')
        elif command == '3':
            if type_id == '22':
                index = connected_devices.index(device)
                connected_devices[index].update_last_seen()

    client.subscribe(topics)
    client.on_message = on_message


def handle_message(update: Update, context: CallbackContext, nodeRed: str = None):
    global chat_id
    if not nodeRed:
        chat_id = update.effective_chat.id
        message_text = update.message.text
        bot = context.bot
        logging.log(logging.INFO, f'Received from app: {message_text}')
    else:
        if chat_id:
            chat_id = chat_id
            message_text = nodeRed
            bot = telegram.Bot(token=env.TELEGRAM_BOT_TOKEN)
            logging.log(logging.INFO, f'Received from NodeRed: {message_text}')
        else:
            return

    if message_text.count('/') < 5:
        bot.send_message(chat_id=chat_id, text=f'{{"req": "{message_text}", "res": {{"status": false, "message": "Invalid request"}}}}')
        return
    _, home_id, node_id, device_id, action, params = message_text.split('/')

    match action:
        case 'status':
            requests = params.split('?')[1:]
            device = Device(home_id, node_id, device_id, None, None)

            if home_id != '*' and node_id != '*' and device_id != '*' and device in connected_devices:
                index = connected_devices.index(device)
                response = connected_devices[index].get_dump_values(requests)
                connected_devices[index].save_values()
                bot.send_message(chat_id=chat_id, text=f'{{"req": "{message_text}", "res": {response}}}')
            else:
                bot.send_message(chat_id=chat_id, text=f'{{"req": "{message_text}", "res": {{"status": false}}}}')
        case 'statusAll':
            if params.strip():
                value_types = params.split('?')
                if len(value_types) != 2:
                    bot.send_message(chat_id=chat_id, text=f'{{"req": "{message_text}", "res": {{"status": false}}}}')
                    return

                value_type = value_types[1]
                device = Device(home_id, node_id, device_id, None, None)

                if home_id != '*' and node_id != '*' and device_id != '*' and device in connected_devices:
                    index = connected_devices.index(device)
                    response = connected_devices[index].get_historical_values(value_type)
                    bot.send_message(chat_id=chat_id, text=f'{{"req": "{message_text}", "res": {response}}}')
                else:
                    bot.send_message(chat_id=chat_id, text=f'{{"req": "{message_text}", "res": {{"status": false}}}}')
            else:
                bot.send_message(chat_id=chat_id, text=f'{{"req": "{message_text}", "res": {{"status": false}}}}')
        case 'set':
            if params.strip():
                result = True
                response = True
                action_params = params.split('?')[1]
                action_pairs = action_params.split('&')
                device_type = params.split('?')[2].split('TYPE=')[1] if len(params.split('?')) == 3 else None

                if len(action_pairs) == 0:
                    bot.send_message(chat_id=chat_id, text=f'{{"req": "{message_text}", "res": {{"status": false}}}}')
                    return
                elif len(action_pairs) == 1:
                    action_type, action_payload = action_pairs[0].split('=')
                    action_pair = action_pairs[0]

                    possible_devices = [device for device in connected_devices if action_type in device.values and device_type == device.device_type] if device_type else [device for device in connected_devices if action_type in device.values]
                    match home_id:
                        case '*':
                            for device in possible_devices:
                                if device.get_value(action_type) == action_payload:
                                    response = False
                                result = result and publish_message(client, device.location, device.node_id,
                                                                    device.device_id, True,
                                                                    action_pair)
                        case _:
                            match node_id:
                                case '*':
                                    for device in [device for device in possible_devices if device.location == home_id]:
                                        if device.get_value(action_type) == action_payload:
                                            response = False
                                        result = result and publish_message(client, device.location, device.node_id,
                                                                            device.device_id,
                                                                            True, action_pair)
                                case _:
                                    match device_id:
                                        case '*':
                                            for device in [device for device in possible_devices if
                                                           device.location == home_id and device.node_id == node_id]:
                                                if device.get_value(action_type) == action_payload:
                                                    response = False
                                                result = result and publish_message(client, device.location,
                                                                                    device.node_id,
                                                                                    device.device_id, True, action_pair)
                                        case _:
                                            for device in [device for device in possible_devices if
                                                           device.location == home_id and device.node_id == node_id and device.device_id == device_id]:
                                                if device.get_value(action_type) == action_payload:
                                                    response = False
                                                result = publish_message(client, home_id, node_id, device_id, True,
                                                                         action_pair)
                else:
                    device = Device(home_id, node_id, device_id, None, None)
                    if home_id != '*' and node_id != '*' and device_id != '*' and device in connected_devices:
                        for action_pair in action_pairs:
                            result = result and publish_message(client, home_id, node_id, device_id, True, action_pair)
                            print(result)
                    else:
                        bot.send_message(chat_id=chat_id,
                                         text=f'{{"req": "{message_text}", "res": {{"status": false}}}}')

                if nodeRed:
                    if response:
                        bot.send_message(chat_id=chat_id,
                                         text=f'{{"req": "{message_text}", "res": {{"status": {"true" if result else "false"}}}}}')
                else:
                    bot.send_message(chat_id=chat_id,
                                     text=f'{{"req": "{message_text}", "res": {{"status": {"true" if result else "false"}}}}}')
            else:
                bot.send_message(chat_id=chat_id, text=f'{{"req": "{message_text}", "res": {{"status": false}}}}')
        case 'get':
            match home_id:
                case '*':
                    bot.send_message(chat_id=chat_id, text=f'{{"req": "{message_text}", "res": {connected_devices}}}')
                case _:
                    match node_id:
                        case '*':
                            bot.send_message(chat_id=chat_id,
                                             text=f'{{"req": "{message_text}", "res": {[device for device in connected_devices if device.location == home_id]}}}')
                        case _:
                            match device_id:
                                case '*':
                                    if device_id == '*':
                                        bot.send_message(chat_id=chat_id,
                                                         text=f'{{"req": "{message_text}", "res": {[device for device in connected_devices if device.location == home_id and device.node_id == node_id]}}}')
                                case _:
                                    device = Device(home_id, node_id, device_id, None, None)
                                    if device in connected_devices:
                                        index = connected_devices.index(Device(home_id, node_id, device_id, None, None))
                                        bot.send_message(chat_id=chat_id,
                                                         text=f'{{"req": "{message_text}", "res": {connected_devices[index]}}}')
        case 'setSchedule':
            requests = params.split('?')[1]
            try:
                schedule = generate_new_schedule(home_id, node_id, device_id, requests)
                schedule_json = json.dumps(schedule)
                publish_to_nodeRED("updateSchedule", schedule_json)

                for device in connected_devices:
                    if device.location == home_id and device.node_id == node_id and device.device_id == device_id:
                        if requests == "action=remove":
                            device.update_schedule(dict())
                        else:
                            readable_schedule = generate_readable_scheduler(home_id, node_id, device_id, requests)
                            device.update_schedule(readable_schedule)
                bot.send_message(chat_id=chat_id, text=f'{{"req": "{message_text}", "res": {{"status": true}}}}')

            except Exception as err:
                print(repr(err))
                bot.send_message(chat_id=chat_id, text=f'{{"req": "{message_text}", "res": {{"status": false}}}}')
        case 'raw':
            publish_raw(client, message_text)
        case _:
            bot.send_message(chat_id=chat_id, text='Unknown command')


def error_handler(update: Update, context: CallbackContext) -> None:
    logging.error(msg="Exception while handling an update:", exc_info=context.error)

    context.bot.send_message(chat_id=chat_id, text=f'{{"req": "{update.message.text}", "res": {{"status": false}}}}')


def check_connected():
    bot = telegram.Bot(token=env.TELEGRAM_BOT_TOKEN)

    while True:
        for device in connected_devices:
            publish_raw(client, f'{device.location}-in/{device.node_id}/{device.device_id}/3/0/18:0')
        for device in connected_devices:
            if time.time() - device.last_seen > 120:
                connected_devices.remove(device)
                bot.send_message(chat_id=chat_id,
                                 text=f'{{"req": "/{device.location}/{device.node_id}/{device.device_id}/disconnected/", "res": {{"device": {device}}}}}')
        time.sleep(30)


def update_values():
    while True:
        for device in connected_devices:
            for value_type in device.values:
                publish_raw(client,
                            f'{device.location}-in/{device.node_id}/{device.device_id}/2/0/{ActionType[value_type].value[0]}:0')
        time.sleep(3)


def shutdown(signum, frame):
    subprocess.run('sudo systemctl stop mysgw.service', shell=True, text=True, check=True)
    subprocess.run('node-red-stop', shell=True, text=True, check=True)
    sys.exit(0)


if __name__ == '__main__':
    updater = Updater(token=env.TELEGRAM_BOT_TOKEN)
    dispatcher = updater.dispatcher
    client = connect_mqtt(env.BROKER_IP)
    client.loop_start()

    dispatcher.add_handler(MessageHandler(Filters.text, handle_message))
    dispatcher.add_error_handler(error_handler)
    con = threading.Thread(target=check_connected)
    con.start()
    upd = threading.Thread(target=update_values)
    upd.start()

    subprocess.run('sudo systemctl restart mysgw.service', shell=True, text=True, check=True)
    subprocess.run('node-red-restart', shell=True, text=True, check=True)
    atexit.register(shutdown, None, None)
    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    updater.start_polling()
