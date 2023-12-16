import argparse
import subprocess


def parse_args():
    parser = argparse.ArgumentParser(description='Script for setting up HOME on raspberry pi')
    parser.add_argument('--python_path', type=str,
                        help='path to python3, e.g. /usr/bin/python3, minimal required version is 3.10',
                        default='/usr/bin/python3', required=True)
    parser.add_argument('--telegram_bot_token', type=str, help='token for telegram bot', required=True)
    parser.add_argument('--location', type=str, help='name of the location', required=True)
    parser.add_argument('--install_mqtt', help='install mqtt broker', action='store_true')
    parser.add_argument('--install_node_red', help='install node red', action='store_true')
    parser.add_argument('--install_mysensors', help='install mysensors', action='store_true')

    return parser.parse_args()


def install_requirements(python_path):
    print('Installing requirements')
    subprocess.run(f'{python_path} -m pip install paho-mqtt python-telegram-bot==13.15', shell=True, text=True,
                   check=True)


def install_mqtt():
    print('Installing MQTT broker')
    subprocess.run('sudo apt-get install mosquitto', shell=True, text=True, check=True)
    subprocess.run(
        'sudo grep -qxF \'allow_anonymous true\' /etc/mosquitto/mosquitto.conf || echo \'allow_anonymous true\' >> /etc/mosquitto/mosquitto.conf',
        shell=True, text=True, check=True)
    subprocess.run(
        'sudo grep -qxF \'listener 1883\' /etc/mosquitto/mosquitto.conf || echo \'listener 1883\' >> /etc/mosquitto/mosquitto.conf',
        shell=True, text=True, check=True)
    subprocess.run('sudo systemctl enable mosquitto', shell=True, text=True, check=True)
    subprocess.run('sudo systemctl restart mosquitto', shell=True, text=True, check=True)


def install_node_red():
    print('Installing Node-Red')
    subprocess.run('bash <(curl -sL https://raw.githubusercontent.com/node-red/linux-installers/master/deb/update-nodejs-and-nodered)', shell=True, text=True, check=True)


def install_mysensors(location):
    print('Installing MySensors')
    subprocess.run('sudo apt-get install git', shell=True, text=True, check=True)
    subprocess.run('git clone https://github.com/mysensors/MySensors.git --branch development', shell=True, text=True, check=True)
    subprocess.run('cd MySensors', shell=True, text=True, check=True)
    subprocess.run(f'sudo ./configure --my-transport=rf24 --my-rf24-irq-pin=15 --my-gateway=mqtt --my-controller-ip-address=localhost --my-mqtt-publish-topic-prefix={location}-out --my-mqtt-subscribe-topic-prefix={location}-in --my-mqtt-client-id={location}', shell=True, text=True, check=True)
    subprocess.run('sudo make', shell=True, text=True, check=True)
    subprocess.run('sudo make install', shell=True, text=True, check=True)


def configure_telegram_bot(token, location):
    print('Configuring telegram bot')
    subprocess.run('> env.py', shell=True, text=True, check=True)
    subprocess.run(f'echo \'TELEGRAM_BOT_TOKEN = \"{token}\"\' >> env.py', shell=True, text=True, check=True)
    subprocess.run(f'echo \'LOCATION = \"{location}\"\' >> env.py', shell=True, text=True, check=True)
    subprocess.run(f'echo \'BROKER_IP = \"localhost\"\' >> env.py', shell=True, text=True, check=True)



if __name__ == '__main__':
    args = parse_args()

    install_requirements(args.python_path)
    if args.install_mqtt:
        install_mqtt()
    if args.install_node_red:
        install_node_red()
    if args.install_mysensors:
        install_mysensors(args.location)
    configure_telegram_bot(args.telegram_bot_token, args.location)





