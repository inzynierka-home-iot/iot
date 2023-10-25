#include <WiFi.h>
#include <PubSubClient.h>
#include <ezButton.h>
#include <OneWire.h>
#include <DallasTemperature.h>

#define PUBLISH_TOPIC_PREFIX "home-1-out"
#define SUBSCRIBE_TOPIC_PREFIX "home-1-in"

const char* ssid = ""; // wifi network ssid
const char* password = ""; // wifi network password
const char* mqtt_server = ""; // raspberrypi ip address
const char* deviceName = "node-2"; 

const int ledPinYellow = 23;

WiFiClient espClient;
PubSubClient client(espClient);
unsigned long tempPreviousTime = 0;

char msgBuff[30];
char topicBuff[30];

void present_initial_values() {
  sprintf(topicBuff, "%s/1/0/1/0/2", PUBLISH_TOPIC_PREFIX);
  sprintf(msgBuff, "%d", digitalRead(ledPinYellow));
  client.publish(topicBuff, msgBuff);
}

void presentation() {
  sprintf(topicBuff, "%s/2/0/0/0/3", PUBLISH_TOPIC_PREFIX);
  client.publish(topicBuff, "Yellow LED");

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
  if (topic == "home-1-in/2/0/1/0/2") {
    digitalWrite(ledPinYellow, payloadString == "1" ? HIGH : LOW);
    sprintf(topicBuff, "%s/1/0/1/0/2", PUBLISH_TOPIC_PREFIX); 
    sprintf(msgBuff, "%d", digitalRead(ledPinYellow));
    client.publish(topicBuff, msgBuff);
  }

  // request
  if (topic == "home-1-in/2/0/2/0/2") {
    sprintf(topicBuff, "%s/1/0/1/0/2", PUBLISH_TOPIC_PREFIX);
    sprintf(msgBuff, "%d", digitalRead(ledPinYellow));
    client.publish(topicBuff, msgBuff);
  }

    // heartbeat
  if (topic == "home-1-in/2/0/3/0/18") {
    sprintf(topicBuff, "%s/2/0/3/0/22", PUBLISH_TOPIC_PREFIX);
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
  pinMode(ledPinYellow, OUTPUT);
  setUpWifi(); 
  delay(1000);
  client.setServer(mqtt_server, 1883);
  client.connect(deviceName); 

  sprintf(topicBuff, "%s/2/#", SUBSCRIBE_TOPIC_PREFIX);
  client.subscribe(topicBuff);
  client.setCallback(receiveMessage); 
  presentation();
}

void loop() {
  if (!client.connected()) {
    reconnect(); 
  }
  if (!client.loop()) {
    client.connect(deviceName);
    if (client.connected()) {
      presentation();
    }
  }
}