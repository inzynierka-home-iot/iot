// Enable debug prints to serial monitor
#define MY_DEBUG

// Enable and select radio type attached
#define MY_RADIO_RF24
//#define MY_RADIO_NRF5_ESB
//#define MY_RADIO_RFM69
//#define MY_RADIO_RFM95

#define MY_NODE_ID 3
#define MY_PARENT_NODE_ID 0

#include <MySensors.h>

#define CHILD_ID_LIGHT 0
#define LIGHT_SENSOR_ANALOG_PIN 35

uint32_t SLEEP_TIME = 30000; // Sleep time between reads (in milliseconds)

MyMessage msg(CHILD_ID_LIGHT, V_LIGHT_LEVEL);
int lastLightLevel;


void presentation() {
	// Send the sketch version information to the gateway and Controller
	sendSketchInfo("Light Sensor", "1.0");

	// Register all sensors to gateway (they will be created as child devices)
	present(CHILD_ID_LIGHT, S_LIGHT_LEVEL, "Light Sensor", true);
}

void setup() {
  present(CHILD_ID_LIGHT, S_LIGHT_LEVEL, "Light Sensor", true);
}

void loop() {
	int16_t lightLevel = analogRead(LIGHT_SENSOR_ANALOG_PIN);
	Serial.println(lightLevel);
	if (lightLevel != lastLightLevel) {
		send(msg.set(lightLevel));
		lastLightLevel = lightLevel;
	}
  sendHeartbeat();
  wait(SLEEP_TIME);
}



