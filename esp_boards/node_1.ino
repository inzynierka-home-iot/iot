#include <WiFi.h>
#include <PubSubClient.h>
#include <ezButton.h>
#include <OneWire.h>
#include <DallasTemperature.h>

const char* ssid = ""; // network name
const char* password = ""; // network password
const char* mqtt_server = "" // RaspberryPi IP address;
const char* deviceName = "NODE-1"; 

const char* debugTopic = "home/debug"; 
const char* ledTopic = "home/led"; 
const char* tempTopic = "home/temp";
const char* buttonTopic = "home/button";
const int ledPin = 15;
const int buttonPin = 23;
const int tempPin = 2;
const int tempDelay = 5000;

WiFiClient espClient;
PubSubClient client(espClient);
ezButton button(buttonPin);
OneWire oneWire(tempPin);
DallasTemperature DS18B20(&oneWire);
unsigned long tempPreviousTime = 0;

float tempC;
char tempMsgBuff[15];

void reconnect() {
  bool ctd = false;

  Serial.println("Disconnected!");
  while (!ctd) {
    Serial.print("Connecting to server...");
    if (client.connect(deviceName)) {
      ctd = true;
      Serial.println("Connected!");
      delay(1000);
      client.publish(debugTopic, "Hello from NODE-1"); 
    } else {
      Serial.println(".");
      delay(1000);
    }
  }
}

void receiveMessage(String topic, byte* payload, unsigned int length) {
  String help;
  Serial.println("Received message:");
  Serial.print("\tTopic: ");
  Serial.println(topic);
  Serial.print("\tPayload: \"");
  for (int i = 0; i < length; i++) {
    Serial.print((char) payload[i]);
    help += (char) payload[i];
  }
  Serial.println("\"");

  if (topic == ledTopic) {
    if (help == "LED1-ON") {
      digitalWrite(ledPin, HIGH);
      Serial.println("LED1: ON"); 
    } else if (help == "LED1-OFF") {
      digitalWrite(ledPin, LOW);
      Serial.println("LED1: OFF");
    } else {
      Serial.println("Unknown command");
    }
  }
}

void setUpWifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting with ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("Connected with Wifi.\nESP received IP: ");
  Serial.println(WiFi.localIP());
}

void setup() {
  Serial.begin(115200);
  pinMode(ledPin, OUTPUT);
  button.setDebounceTime(50);
  DS18B20.begin();
  setUpWifi(); 
  delay(1000);
  client.setServer(mqtt_server, 1883);
  client.connect(deviceName); 
  client.subscribe(ledTopic); 
  client.setCallback(receiveMessage); 
  client.publish(debugTopic, "Hello from NODE-1"); 
}

void tempLoop() {
  unsigned long tempCurrentTime = millis();

  if (tempCurrentTime - tempPreviousTime > tempDelay) {
    tempPreviousTime = tempCurrentTime;
    DS18B20.requestTemperatures();
    tempC = DS18B20.getTempCByIndex(0);
    sprintf(tempMsgBuff, "TEMP1-%f", tempC);
    Serial.println(tempMsgBuff);
    Serial.println(tempTopic);
    if (client.connected()) {
      client.publish(tempTopic, tempMsgBuff);
    }
  }
}

void buttonLoop() {
  button.loop();
  if (button.isPressed() && client.connected()) {
    client.publish(buttonTopic, "BUTTON1-PRESSED");
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
      client.publish(debugTopic, "Hello from NODE-1"); 
    }
  }
}