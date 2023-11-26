from enum import Enum

class DeviceType(Enum):
    S_DOOR = 0,
    S_MOTION = 1,
    S_SMOKE = 2,
    S_BINARY = 3,
    S_DIMMER = 4,
    S_COVER = 5,
    S_TEMP = 6,
    S_HUM = 7,
    S_BARO = 8,
    S_WIND = 9,
    S_RAIN = 10,
    S_UV = 11,
    S_WEIGHT = 12,
    S_POWER = 13,
    S_HEATER = 14,
    S_DISTANCE = 15,
    S_LIGHT_LEVEL = 16,
    S_ARDUINO_NODE = 17,
    S_ARDUINO_REPEATER_NODE = 18,
    S_LOCK = 19,
    S_IR = 20,
    S_WATER = 21,
    S_AIR_QUALITY = 22,
    S_CUSTOM = 23,
    S_DUST = 24,
    S_SCENE_CONTROLLER = 25,
    S_RGB_LIGHT = 26,
    S_RGBW_LIGHT = 27,
    S_COLOR_SENSOR = 28,
    S_HVAC = 29,
    S_MULTIMETER = 30,
    S_SPRINKLER = 31,
    S_WATER_LEAK = 32,
    S_SOUND = 33,
    S_VIBRATION = 34,
    S_MOISTURE = 35,
    S_INFO = 36,
    S_GAS = 37,
    S_GPS = 38,
    S_WATER_QUALITY = 39,
    S_FAN = 40
