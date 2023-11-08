#include <WiFi.h>
#include <PubSubClient.h>
#include <ezButton.h>
#include <OneWire.h>
#include <DallasTemperature.h>

#define PUBLISH_TOPIC_PREFIX "home-1-out"
#define SUBSCRIBE_TOPIC_PREFIX "home-1-in"

const char* ssid = "";
const char* password = "";
const char* mqtt_server = "";
const char* deviceName = "node-1"; 
const unsigned long delayTime = 60*1000UL;
unsigned long lastMillis = millis();
const unsigned long tempDelayTime = 15*1000UL;
unsigned long tempLastMillis = millis();

const int ledPinGreen = 15;
const int ledPinYellow = 22;
const int ledPinRed = 23;
const int buttonPin = 4;
const int tempPin = 2;
const int fanTempPin = 18;
const int fanSpeedPin = 19;
const int fanDirectionPin = 21;

int fanTempValue = 0;
int fanSpeedValue = 0;
int fanDirectionValue = 0;

WiFiClient espClient;
PubSubClient client(espClient);
ezButton button(buttonPin);
OneWire oneWire(tempPin);
DallasTemperature DS18B20(&oneWire);

float tempC;
char msgBuff[30];
char topicBuff[30];
bool lockStatus = false;

void send_update() {
  if (millis() - lastMillis > delayTime) {
    lastMillis = millis();
    presentation();
  }
}

void present_initial_values() {
  sprintf(topicBuff, "%s/1/0/1/0/2", PUBLISH_TOPIC_PREFIX);
  sprintf(msgBuff, "%d", digitalRead(ledPinGreen));
  client.publish(topicBuff, msgBuff);

  DS18B20.requestTemperatures();
  tempC = DS18B20.getTempCByIndex(0);
  sprintf(topicBuff, "%s/1/1/1/0/0", PUBLISH_TOPIC_PREFIX);
  sprintf(msgBuff, "%f", tempC);
  client.publish(topicBuff, msgBuff);

  sprintf(topicBuff, "%s/1/2/1/0/2", PUBLISH_TOPIC_PREFIX);
  sprintf(msgBuff, "%d", digitalRead(ledPinYellow));
  client.publish(topicBuff, msgBuff);

  sprintf(topicBuff, "%s/1/3/1/0/2", PUBLISH_TOPIC_PREFIX);
  sprintf(msgBuff, "%d", digitalRead(ledPinRed));
  client.publish(topicBuff, msgBuff);

  sprintf(topicBuff, "%s/1/4/1/0/36", PUBLISH_TOPIC_PREFIX);
  client.publish(topicBuff, lockStatus ? "1" : "0");

  sprintf(topicBuff, "%s/1/5/1/0/0", PUBLISH_TOPIC_PREFIX);
  sprintf(msgBuff, "%d", (int) (fanTempValue / 5));
  client.publish(topicBuff, msgBuff);

  sprintf(topicBuff, "%s/1/5/1/0/3", PUBLISH_TOPIC_PREFIX);
  sprintf(msgBuff, "%d", (int) (fanSpeedValue / 2.5));
  client.publish(topicBuff, msgBuff);

  sprintf(topicBuff, "%s/1/5/1/0/10", PUBLISH_TOPIC_PREFIX);
  sprintf(msgBuff, "%d", fanDirectionValue);
  client.publish(topicBuff, msgBuff);
}

void presentation() {
  sprintf(topicBuff, "%s/1/0/0/0/3", PUBLISH_TOPIC_PREFIX);
  client.publish(topicBuff, "Green LED");
  sprintf(topicBuff, "%s/1/1/0/0/6", PUBLISH_TOPIC_PREFIX);
  client.publish(topicBuff, "Temperature sensor");
  sprintf(topicBuff, "%s/1/2/0/0/3", PUBLISH_TOPIC_PREFIX);
  client.publish(topicBuff, "Yellow LED");
  sprintf(topicBuff, "%s/1/3/0/0/3", PUBLISH_TOPIC_PREFIX);
  client.publish(topicBuff, "Red LED");
  sprintf(topicBuff, "%s/1/4/0/0/19", PUBLISH_TOPIC_PREFIX);
  client.publish(topicBuff, "Button");
  sprintf(topicBuff, "%s/1/5/0/0/40", PUBLISH_TOPIC_PREFIX);
  client.publish(topicBuff, "Fan");

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
  if (topic == "home-1-in/1/0/1/0/2") {
    digitalWrite(ledPinGreen, payloadString == "1" ? HIGH : LOW);
    sprintf(topicBuff, "%s/1/0/1/0/2", PUBLISH_TOPIC_PREFIX);
    sprintf(msgBuff, "%d", digitalRead(ledPinGreen));
    client.publish(topicBuff, msgBuff);
  }
  if (topic == "home-1-in/1/2/1/0/2") {
    digitalWrite(ledPinYellow, payloadString == "1" ? HIGH : LOW);
    sprintf(topicBuff, "%s/1/2/1/0/2", PUBLISH_TOPIC_PREFIX);
    sprintf(msgBuff, "%d", digitalRead(ledPinYellow));
    client.publish(topicBuff, msgBuff);
  }
  if (topic == "home-1-in/1/3/1/0/2") {
    digitalWrite(ledPinRed, payloadString == "1" ? HIGH : LOW);
    sprintf(topicBuff, "%s/1/3/1/0/2", PUBLISH_TOPIC_PREFIX);
    sprintf(msgBuff, "%d", digitalRead(ledPinRed));
    client.publish(topicBuff, msgBuff);
  }
  if (topic == "home-1-in/1/5/1/0/0") {
    fanTempValue = 5 * payloadString.toInt();
    analogWrite(fanTempPin, fanTempValue);
    sprintf(topicBuff, "%s/1/5/1/0/0", PUBLISH_TOPIC_PREFIX);
    sprintf(msgBuff, "%d", (int) (fanTempValue / 5));
    client.publish(topicBuff, msgBuff);
    Serial.println(fanTempValue);
  }
  if (topic == "home-1-in/1/5/1/0/3") {
    fanSpeedValue = (int) 2.5 * payloadString.toInt();
    analogWrite(fanSpeedPin, fanSpeedValue);
    sprintf(topicBuff, "%s/1/5/1/0/3", PUBLISH_TOPIC_PREFIX);
    sprintf(msgBuff, "%d", (int) (fanSpeedValue / 2.5));
    client.publish(topicBuff, msgBuff);
  }
  if (topic == "home-1-in/1/5/1/0/10") {
    fanDirectionValue = payloadString.toInt();
    analogWrite(fanDirectionPin, fanDirectionValue);
    sprintf(topicBuff, "%s/1/5/1/0/10", PUBLISH_TOPIC_PREFIX);
    sprintf(msgBuff, "%d", fanDirectionValue);
    client.publish(topicBuff, msgBuff);
  }

  // request
  if (topic == "home-1-in/1/0/2/0/2") {
    sprintf(topicBuff, "%s/1/0/1/0/2", PUBLISH_TOPIC_PREFIX);
    sprintf(msgBuff, "%d", digitalRead(ledPinGreen));
    client.publish(topicBuff, msgBuff);
  }
  if (topic == "home-1-in/1/1/2/0/0") {
    DS18B20.requestTemperatures();
    tempC = DS18B20.getTempCByIndex(0);
    sprintf(topicBuff, "%s/1/1/1/0/0", PUBLISH_TOPIC_PREFIX);
    sprintf(msgBuff, "%f", tempC);
    client.publish(topicBuff, msgBuff);
  }
  if (topic == "home-1-in/1/2/2/0/2") {
    sprintf(topicBuff, "%s/1/2/1/0/2", PUBLISH_TOPIC_PREFIX);
    sprintf(msgBuff, "%d", digitalRead(ledPinYellow));
    client.publish(topicBuff, msgBuff);
  }
  if (topic == "home-1-in/1/3/2/0/2") {
    sprintf(topicBuff, "%s/1/3/1/0/2", PUBLISH_TOPIC_PREFIX);
    sprintf(msgBuff, "%d", digitalRead(ledPinRed));
    client.publish(topicBuff, msgBuff);
  }
  if (topic == "home-1-in/1/4/2/0/36") {
    sprintf(topicBuff, "%s/1/4/1/0/36", PUBLISH_TOPIC_PREFIX);
    client.publish(topicBuff, lockStatus ? "1" : "0");
  }
  if (topic == "home-1-in/1/5/2/0/0") {
    sprintf(topicBuff, "%s/1/5/1/0/0", PUBLISH_TOPIC_PREFIX);
    sprintf(msgBuff, "%d", (int) (fanTempValue / 5));
    client.publish(topicBuff, msgBuff);
  }
  if (topic == "home-1-in/1/5/2/0/3") {
    sprintf(topicBuff, "%s/1/5/1/0/3", PUBLISH_TOPIC_PREFIX);
    sprintf(msgBuff, "%d", (int) (fanSpeedValue / 2.5));
    client.publish(topicBuff, msgBuff);
  }
  if (topic == "home-1-in/1/5/2/0/10") {
    sprintf(topicBuff, "%s/1/5/1/0/10", PUBLISH_TOPIC_PREFIX);
    sprintf(msgBuff, "%d", fanDirectionValue);
    client.publish(topicBuff, msgBuff);
  }

  // heartbeat
  if (topic == "home-1-in/1/0/3/0/18") {
    sprintf(topicBuff, "%s/1/0/3/0/22", PUBLISH_TOPIC_PREFIX);
    client.publish(topicBuff, "");
  }
  if (topic == "home-1-in/1/1/3/0/18") {
    sprintf(topicBuff, "%s/1/1/3/0/22", PUBLISH_TOPIC_PREFIX);
    client.publish(topicBuff, "");
  }
  if (topic == "home-1-in/1/2/3/0/18") {
    sprintf(topicBuff, "%s/1/2/3/0/22", PUBLISH_TOPIC_PREFIX);
    client.publish(topicBuff, "");
  }
  if (topic == "home-1-in/1/3/3/0/18") {
    sprintf(topicBuff, "%s/1/3/3/0/22", PUBLISH_TOPIC_PREFIX);
    client.publish(topicBuff, "");
  }
  if (topic == "home-1-in/1/4/3/0/18") {
    sprintf(topicBuff, "%s/1/4/3/0/22", PUBLISH_TOPIC_PREFIX);
    client.publish(topicBuff, "");
  }
  if (topic == "home-1-in/1/5/3/0/18") {
    sprintf(topicBuff, "%s/1/5/3/0/22", PUBLISH_TOPIC_PREFIX);
    client.publish(topicBuff, "");
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
  pinMode(ledPinGreen, OUTPUT);
  pinMode(ledPinYellow, OUTPUT);
  pinMode(ledPinRed, OUTPUT);
  pinMode(fanTempPin, OUTPUT);
  pinMode(fanSpeedPin, OUTPUT);
  pinMode(fanDirectionPin, OUTPUT);
  button.setDebounceTime(50);
  DS18B20.begin();
  setUpWifi(); 
  delay(1000);
  client.setServer(mqtt_server, 1883);
  client.connect(deviceName); 

  sprintf(topicBuff, "%s/1/#", SUBSCRIBE_TOPIC_PREFIX);
  client.subscribe(topicBuff);
  client.setCallback(receiveMessage); 
  presentation();
}

void tempLoop() {
  if (millis() - tempLastMillis > tempDelayTime) {
    tempLastMillis = millis();
    DS18B20.requestTemperatures();
    tempC = DS18B20.getTempCByIndex(0);
    if (client.connected()) {
      sprintf(msgBuff, "%f", tempC);
      sprintf(topicBuff, "%s/1/1/1/0/0", PUBLISH_TOPIC_PREFIX);
      client.publish(topicBuff, msgBuff);
    }
  }
}

void buttonLoop() {
  button.loop();
  if (button.isPressed() && client.connected()) {
    lockStatus = !lockStatus;
    sprintf(topicBuff, "%s/1/4/1/0/36", PUBLISH_TOPIC_PREFIX);
    client.publish(topicBuff, lockStatus ? "1" : "0");
    Serial.println("Button pressed");
  }
}

void loop() {
  buttonLoop();
  tempLoop();
  

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