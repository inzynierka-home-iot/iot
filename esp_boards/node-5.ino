#define MY_DEBUG

// Enable and select radio type attached
#define MY_RADIO_RF24
//#define MY_RADIO_NRF5_ESB
//#define MY_RADIO_RFM69
//#define MY_RADIO_RFM95

#define MY_NODE_ID 5
#define MY_PARENT_NODE_ID 0

#include <MySensors.h>

#define CHILD_ID_MOTION 0
#define MOTION_INPUT_PIN 3

unsigned long lastMillis = millis();
uint32_t SLEEP_TIME = 5000; // Sleep time between reads (in milliseconds)

const unsigned long motionSensorDelayTime = 1000UL;
unsigned long motionSensorLastMillis = millis();
int motionSensorStatusPrevious = LOW;
int motionSensorStatusCurrent = LOW;

MyMessage msg(CHILD_ID_MOTION, V_TRIPPED);


void presentation() {
	// Send the sketch version information to the gateway and Controller
	sendSketchInfo("Czujnik ruchu", "1.0");

	// Register all sensors to gateway (they will be created as child devices)
	present(CHILD_ID_MOTION, S_MOTION, "Czujnik ruchu", true);
}

void setup() {
  pinMode(MOTION_INPUT_PIN, INPUT);
  present(CHILD_ID_MOTION, S_MOTION, "Czujnik ruchu", true);
}

void loop() {
  if (millis() - motionSensorLastMillis > motionSensorDelayTime) {
    motionSensorLastMillis = millis();
    motionSensorStatusPrevious = motionSensorStatusCurrent;
    motionSensorStatusCurrent = digitalRead(MOTION_INPUT_PIN);
    if (motionSensorStatusPrevious == LOW && motionSensorStatusCurrent == HIGH) {
      send(msg.set("1"));
      Serial.println("motion detected");
    } else if (motionSensorStatusPrevious == HIGH && motionSensorStatusCurrent == LOW) {
      send(msg.set("0"));
      Serial.println("motion stopped");
    }
  }

  if (millis() - lastMillis > SLEEP_TIME) {
    lastMillis = millis();
    sendHeartbeat();
    present(CHILD_ID_MOTION, S_MOTION, "Czujnik ruchu", true);
  }
}


