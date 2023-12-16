#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>

#define PUBLISH_TOPIC_PREFIX "home-1-out"
#define SUBSCRIBE_TOPIC_PREFIX "home-1-in"

const char *ssid = "";
const char *password = "";
const char* mqtt_server = "";

const char* deviceName = "node-2"; 
const unsigned long delayTime = 60*1000UL;
unsigned long lastMillis = millis();
const unsigned long dhtDelayTime =  15*1000UL;
unsigned long dhtLastMillis = millis();

const int redPin = 21;
const int greenPin = 22;
const int bluePin = 23;
const int dhtPin = 32;
const int ledPinRed = 15;

int redValue = 5;
int greenValue = 30;
int blueValue = 210;

float humi;

WiFiClient espClient;
PubSubClient client(espClient);
DHT dht(dhtPin, DHT11);

char msgBuff[30];
char topicBuff[30];

void send_update() {
  if (millis() - lastMillis > delayTime) {
    lastMillis = millis();
    presentation();
  }
}

void get_hex_msg() {
  sprintf(msgBuff, "%s%s%s%s%s%s", 
    redValue < 16 ? "0" : "",
    String(redValue, HEX),
    greenValue < 16 ? "0" : "",
    String(greenValue, HEX),
    blueValue < 16 ? "0" : "",
    String(blueValue, HEX));
}

int get_int_from_hex(char hex1, char hex2) {
  char hex[2] = {hex1, hex2};
  return (int) strtol(hex, NULL, 16);
}

void present_initial_values() {
  sprintf(topicBuff, "%s/2/0/1/0/40", PUBLISH_TOPIC_PREFIX);
  get_hex_msg();
  client.publish(topicBuff, msgBuff);

  humi = dht.readHumidity();
  sprintf(topicBuff, "%s/2/1/1/0/1", PUBLISH_TOPIC_PREFIX);
  sprintf(msgBuff, "%f", humi);
  client.publish(topicBuff, msgBuff);

  sprintf(topicBuff, "%s/2/2/1/0/2", PUBLISH_TOPIC_PREFIX);
  sprintf(msgBuff, "%d", digitalRead(ledPinRed));
  client.publish(topicBuff, msgBuff);
}

void presentation() {
  sprintf(topicBuff, "%s/2/0/0/0/26", PUBLISH_TOPIC_PREFIX);
  client.publish(topicBuff, "RGB LED");
  sprintf(topicBuff, "%s/2/1/0/0/7", PUBLISH_TOPIC_PREFIX);
  client.publish(topicBuff, "Czujnik wilgotnosci");
  sprintf(topicBuff, "%s/2/2/0/0/3", PUBLISH_TOPIC_PREFIX);
  client.publish(topicBuff, "Czerwony LED");

  present_initial_values();
}

void reconnect() {
  bool ctd = false;

  Serial.println("Disconnected!");
  while (!ctd) {
    Serial.print("Connecting to server...");
    if (client.connect(deviceName)) {
      ctd = true;
      Serial.println("Connected!");
    } else {
      Serial.println(".");
      delay(1000);
    }
  }
}

void receiveMessage(String topic, byte* payload, unsigned int length) {
  String payloadString;
  Serial.println("Received message:");
  Serial.print("\tTopic: ");
  Serial.println(topic);
  Serial.print("\tPayload: \"");
  for (int i = 0; i < length; i++) {
    Serial.print((char) payload[i]);
    payloadString += (char) payload[i];
  }
  Serial.println("\"");

  // set
  if (topic == "home-1-in/2/0/1/0/40") {
    analogWrite(redPin, get_int_from_hex(payloadString[0], payloadString[1]));
    redValue = get_int_from_hex(payloadString[0], payloadString[1]);
    analogWrite(greenPin, get_int_from_hex(payloadString[2], payloadString[3]));
    greenValue = get_int_from_hex(payloadString[2], payloadString[3]);
    analogWrite(bluePin, get_int_from_hex(payloadString[4], payloadString[5]));
    blueValue = get_int_from_hex(payloadString[4], payloadString[5]);
    sprintf(topicBuff, "%s/2/0/1/0/40", PUBLISH_TOPIC_PREFIX); 
    get_hex_msg();
    client.publish(topicBuff, msgBuff);
  }
  if (topic == "home-1-in/2/2/1/0/2") {
    digitalWrite(ledPinRed, payloadString == "1" ? HIGH : LOW);
    sprintf(topicBuff, "%s/2/2/1/0/2", PUBLISH_TOPIC_PREFIX);
    sprintf(msgBuff, "%d", digitalRead(ledPinRed));
    client.publish(topicBuff, msgBuff);
  }

  // request
  if (topic == "home-1-in/2/0/2/0/40") {
    sprintf(topicBuff, "%s/2/0/1/0/40", PUBLISH_TOPIC_PREFIX);
    get_hex_msg();
    client.publish(topicBuff, msgBuff);
  }
  if (topic == "home-1-in/2/1/2/0/1") {
    humi = dht.readHumidity();
    sprintf(topicBuff, "%s/2/1/1/0/1", PUBLISH_TOPIC_PREFIX);
    sprintf(msgBuff, "%f", humi);
    client.publish(topicBuff, msgBuff);
  }
  if (topic == "home-1-in/2/2/2/0/2") {
    sprintf(topicBuff, "%s/2/2/1/0/2", PUBLISH_TOPIC_PREFIX);
    sprintf(msgBuff, "%d", digitalRead(ledPinRed));
    client.publish(topicBuff, msgBuff);
  }

  // heartbeat
  if (topic == "home-1-in/2/0/3/0/18") {
    sprintf(topicBuff, "%s/2/0/3/0/22", PUBLISH_TOPIC_PREFIX);
    client.publish(topicBuff, "1");
  }
  if (topic == "home-1-in/2/1/3/0/18") {
    sprintf(topicBuff, "%s/2/1/3/0/22", PUBLISH_TOPIC_PREFIX);
    client.publish(topicBuff, "1");
  }
  if (topic == "home-1-in/2/2/3/0/18") {
    sprintf(topicBuff, "%s/2/2/3/0/22", PUBLISH_TOPIC_PREFIX);
    client.publish(topicBuff, "1");
  }
}

void setUpWifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting with ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print("Connecting with ");
    Serial.println(ssid);
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("Connected with Wifi.\nESP received IP: ");
  Serial.println(WiFi.localIP());
}

void setup() {
  Serial.begin(115200);
  pinMode(redPin, OUTPUT);
  pinMode(greenPin, OUTPUT);
  pinMode(bluePin, OUTPUT);
  pinMode(ledPinRed, OUTPUT);
  analogWrite(redPin, redValue);
  analogWrite(greenPin, greenValue);
  analogWrite(bluePin, blueValue);
  dht.begin();
  setUpWifi(); 
  delay(1000);
  client.setServer(mqtt_server, 1883);
  client.connect(deviceName); 

  sprintf(topicBuff, "%s/2/#", SUBSCRIBE_TOPIC_PREFIX);
  client.subscribe(topicBuff);
  client.setCallback(receiveMessage); 
  presentation();
}

void dhtLoop() {
  if (millis() - dhtLastMillis > dhtDelayTime) {
    dhtLastMillis = millis();
    humi = dht.readHumidity();
    if (client.connected()) {
      sprintf(msgBuff, "%f", humi);
      sprintf(topicBuff, "%s/2/1/1/0/1", PUBLISH_TOPIC_PREFIX);
      client.publish(topicBuff, msgBuff);
    }
  }
}

void loop() {
  dhtLoop();

  if (!client.connected()) {
    reconnect(); 
  }
  if (!client.loop()) {
    client.connect(deviceName);
    if (client.connected()) {
      presentation();
    }
  }
  send_update();
}