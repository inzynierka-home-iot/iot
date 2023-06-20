from paho.mqtt import client as mqtt_client

port = 1883
led_topic = 'home/led'
temp_topic = 'home/temp'
button_topic = 'home/button'
debug_topic = 'home/debug'
client_id = 'python-mqtt'
temp = ''
button_clicked = False


def connect_mqtt(broker) -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
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


def subscribe_temp(client, topic):
    def on_message(client, userdata, msg):
        global temp
        temp = msg.payload.decode().split('-')[1]
        print(f'Received message {msg.payload.decode()} from topic {topic} with temp {temp}')
        print(get_temp())

    client.subscribe(topic)
    client.on_message = on_message


def get_temp():
    return temp


def subscribe_button(client, topic):
    def on_message(client, userdata, msg):
        global button_clicked
        button_clicked = True
        print(f'Received message {msg.payload.decode()} from topic {topic}')
        print(get_button())

    client.subscribe(topic)
    client.on_message = on_message


def run(client):
    subscribe_temp(client, temp_topic)
    subscribe_button(client, button_topic)
    client.loop_start()
