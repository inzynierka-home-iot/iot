#include <WiFi.h>
#include <PubSubClient.h>
#include <NewPing.h>

#define PUBLISH_TOPIC_PREFIX "home-1-out"
#define SUBSCRIBE_TOPIC_PREFIX "home-1-in"


const char *ssid = "";
const char *password = "";
const char* mqtt_server = "";

const char* deviceName = "node-3";
const unsigned long delayTime = 60*1000UL;
unsigned long lastMillis = millis();
const unsigned long distanceSensorDelayTime = 5000UL;
unsigned long distanceSensorLastMillis = millis();
unsigned long distanceSensorMaxDistance = 400;
// const unsigned long motionSensorDelayTime = 1000UL;
// unsigned long motionSensorLastMillis = millis();

// const int lightSensorPin = 35;
const int buzzerPin = 13;
// const int motionSensorPin = 12;
const int distanceSensorTriggerPin = 26;
const int distanceSensorEchoPin = 25;

WiFiClient espClient;
PubSubClient client(espClient);
NewPing sonar(distanceSensorTriggerPin, distanceSensorEchoPin, distanceSensorMaxDistance);

char msgBuff[30];
char topicBuff[30];

bool buzzerStatus = false;
// int motionSensorStatusPrevious = LOW;
// int motionSensorStatusCurrent = LOW;
int distanceSensorLastDistance = 0;

void send_update() {
  if (millis() - lastMillis > delayTime) {
    lastMillis = millis();
    presentation();
  }
}

void present_initial_values() {
  // sprintf(topicBuff, "%s/3/0/1/0/23", PUBLISH_TOPIC_PREFIX);
  // sprintf(msgBuff, "%d", analogRead(lightSensorPin));
  // client.publish(topicBuff, msgBuff);

  sprintf(topicBuff, "%s/3/0/1/0/2", PUBLISH_TOPIC_PREFIX);
  sprintf(msgBuff, "%d", digitalRead(buzzerPin));
  client.publish(topicBuff, msgBuff);

  // sprintf(topicBuff, "%s/3/1/1/0/16", PUBLISH_TOPIC_PREFIX);
  // sprintf(msgBuff, "%d", digitalRead(motionSensorPin));
  // client.publish(topicBuff, msgBuff);

  sprintf(topicBuff, "%s/3/1/1/0/13", PUBLISH_TOPIC_PREFIX);
  sprintf(msgBuff, "%d", distanceSensorLastDistance);
  client.publish(topicBuff, msgBuff);
}

void presentation() {
  // sprintf(topicBuff, "%s/3/0/0/0/16", PUBLISH_TOPIC_PREFIX);
  // client.publish(topicBuff, "Czujnik natezenia swiatla");
  sprintf(topicBuff, "%s/3/0/0/0/23", PUBLISH_TOPIC_PREFIX);
  client.publish(topicBuff, "Brzeczyk");
  // sprintf(topicBuff, "%s/3/1/0/0/1", PUBLISH_TOPIC_PREFIX);
  // client.publish(topicBuff, "Czujnik ruchu");
  sprintf(topicBuff, "%s/3/1/0/0/15", PUBLISH_TOPIC_PREFIX);
  client.publish(topicBuff, "Czujnik odleglosci");

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
  if (topic == "home-1-in/3/0/1/0/2") {
    digitalWrite(buzzerPin, payloadString == "1" ? HIGH : LOW);
    buzzerStatus = payloadString == "1" ? true : false;
    sprintf(topicBuff, "%s/3/0/1/0/2", PUBLISH_TOPIC_PREFIX);
    sprintf(msgBuff, "%d", digitalRead(buzzerPin));
    client.publish(topicBuff, msgBuff);
  }

  // request
  // if (topic == "home-1-in/3/0/2/0/23") {
  //   sprintf(topicBuff, "%s/3/0/1/0/23", PUBLISH_TOPIC_PREFIX);
  //   sprintf(msgBuff, "%d", analogRead(lightSensorPin));
  //   client.publish(topicBuff, msgBuff);
  // }
  if (topic == "home-1-in/3/0/2/0/2") {
    sprintf(topicBuff, "%s/3/0/1/0/2", PUBLISH_TOPIC_PREFIX);
    sprintf(msgBuff, "%d", digitalRead(buzzerPin));
    client.publish(topicBuff, msgBuff);
  }
  // if (topic == "home-1-in/3/1/2/0/16") {
  //   sprintf(topicBuff, "%s/3/1/1/0/16", PUBLISH_TOPIC_PREFIX);
  //   sprintf(msgBuff, "%d", digitalRead(motionSensorPin));
  //   client.publish(topicBuff, msgBuff);
  // }
  if (topic == "home-1-in/3/1/2/0/13") {
    sprintf(topicBuff, "%s/3/1/1/0/13", PUBLISH_TOPIC_PREFIX);
    sprintf(msgBuff, "%d", distanceSensorLastDistance);
    client.publish(topicBuff, msgBuff);
  }

  // heartbeat
  // if (topic == "home-1-in/3/0/3/0/18") {
  //   sprintf(topicBuff, "%s/3/0/3/0/22", PUBLISH_TOPIC_PREFIX);
  //   client.publish(topicBuff, "1");
  // }
  if (topic == "home-1-in/3/0/3/0/18") {
    sprintf(topicBuff, "%s/3/0/3/0/22", PUBLISH_TOPIC_PREFIX);
    client.publish(topicBuff, "1");
  }
  // if (topic == "home-1-in/3/1/3/0/18") {
  //   sprintf(topicBuff, "%s/3/1/3/0/22", PUBLISH_TOPIC_PREFIX);
  //   client.publish(topicBuff, "1");
  // }
  if (topic == "home-1-in/3/1/3/0/18") {
    sprintf(topicBuff, "%s/3/1/3/0/22", PUBLISH_TOPIC_PREFIX);
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
  pinMode(buzzerPin, OUTPUT);
  // pinMode(lightSensorPin, INPUT);
  // pinMode(motionSensorPin, INPUT);
  setUpWifi(); 
  delay(1000);
  client.setServer(mqtt_server, 1883);
  client.connect(deviceName); 

  sprintf(topicBuff, "%s/3/#", SUBSCRIBE_TOPIC_PREFIX);
  client.subscribe(topicBuff);
  client.setCallback(receiveMessage); 
  presentation();
}

// void motionSensorLoop() {
//   if (millis() - motionSensorLastMillis > motionSensorDelayTime) {
//     motionSensorLastMillis = millis();
//     motionSensorStatusPrevious = motionSensorStatusCurrent;
//     motionSensorStatusCurrent = digitalRead(motionSensorPin);
//     if (motionSensorStatusPrevious == LOW && motionSensorStatusCurrent == HIGH) {
//       if (client.connected()) {
//         sprintf(topicBuff, "%s/3/1/1/0/16", PUBLISH_TOPIC_PREFIX);
//         client.publish(topicBuff, "1");
//         Serial.println("motion detected");
//       }
//     } else if (motionSensorStatusPrevious == HIGH && motionSensorStatusCurrent == LOW) {
//       if (client.connected()) {
//         sprintf(topicBuff, "%s/3/1/1/0/16", PUBLISH_TOPIC_PREFIX);
//         client.publish(topicBuff, "0");
//         Serial.println("motion stopped");
//       }
//     }
//   }
// }

void distanceSensorLoop() {
  if (millis() - distanceSensorLastMillis > distanceSensorDelayTime) {
    distanceSensorLastMillis = millis();
    int distanceSensorDistance = sonar.ping_cm();
    if (distanceSensorDistance != distanceSensorLastDistance) {
      if (client.connected()) {
        sprintf(topicBuff, "%s/3/2/1/0/13", PUBLISH_TOPIC_PREFIX);
        sprintf(msgBuff, "%d", distanceSensorDistance);
        client.publish(topicBuff, msgBuff);
      }
      distanceSensorLastDistance = distanceSensorDistance;
    } 
  }
}

void loop() {
  // motionSensorLoop();
  distanceSensorLoop();

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
