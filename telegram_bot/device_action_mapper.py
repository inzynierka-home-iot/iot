from device_types import DeviceType
from action_types import ActionType

device_action_dict = {
    DeviceType.S_DOOR.name: [ActionType.V_TRIPPED.name, ActionType.V_ARMED.name],
    DeviceType.S_MOTION.name: [ActionType.V_TRIPPED.name, ActionType.V_ARMED.name],
    DeviceType.S_SMOKE.name: [ActionType.V_TRIPPED.name, ActionType.V_ARMED.name],
    DeviceType.S_BINARY.name: [ActionType.V_STATUS.name, ActionType.V_WATT.name],
    DeviceType.S_DIMMER.name: [ActionType.V_STATUS.name, ActionType.V_PERCENTAGE.name, ActionType.V_WATT.name],
    DeviceType.S_COVER.name: [ActionType.V_UP.name, ActionType.V_DOWN.name, ActionType.V_STOP.name, ActionType.V_PERCENTAGE.name],
    DeviceType.S_TEMP.name: [ActionType.V_TEMP.name, ActionType.V_ID.name],
    DeviceType.S_HUM.name: [ActionType.V_HUM.name],
    DeviceType.S_BARO.name: [ActionType.V_PRESSURE.name, ActionType.V_FORECAST.name],
    DeviceType.S_WIND.name: [ActionType.V_WIND.name, ActionType.V_GUST.name, ActionType.V_DIRECTION.name],
    DeviceType.S_RAIN.name: [ActionType.V_RAIN.name, ActionType.V_RAINRATE.name],
    DeviceType.S_UV.name: [ActionType.V_UV.name],
    DeviceType.S_WEIGHT.name: [ActionType.V_WEIGHT.name, ActionType.V_IMPEDANCE.name],
    DeviceType.S_POWER.name: [ActionType.V_WATT.name, ActionType.V_KWH.name, ActionType.V_VAR.name, ActionType.V_VA.name, ActionType.V_POWER_FACTOR.name],
    DeviceType.S_HEATER.name: [ActionType.V_HVAC_SETPOINT_HEAT.name, ActionType.V_HVAC_FLOW_STATE.name, ActionType.V_TEMP.name, ActionType.V_STATUS.name],
    DeviceType.S_DISTANCE.name: [ActionType.V_DISTANCE.name, ActionType.V_UNIT_PREFIX.name],
    DeviceType.S_LIGHT_LEVEL.name: [ActionType.V_LIGHT_LEVEL.name, ActionType.V_LEVEL.name],
    DeviceType.S_ARDUINO_NODE.name: [],
    DeviceType.S_ARDUINO_REPEATER_NODE.name: [],
    DeviceType.S_LOCK.name: [ActionType.V_LOCK_STATUS.name],
    DeviceType.S_IR.name: [ActionType.V_IR_SEND.name, ActionType.V_IR_RECEIVE.name, ActionType.V_IR_RECORD.name],
    DeviceType.S_WATER.name: [ActionType.V_FLOW.name, ActionType.V_VOLUME.name],
    DeviceType.S_AIR_QUALITY.name: [ActionType.V_LEVEL.name, ActionType.V_UNIT_PREFIX.name],
    DeviceType.S_CUSTOM.name: [ActionType.V_STATUS.name],
    DeviceType.S_DUST.name: [ActionType.V_LEVEL.name, ActionType.V_UNIT_PREFIX.name],
    DeviceType.S_SCENE_CONTROLLER.name: [ActionType.V_SCENE_ON.name, ActionType.V_SCENE_OFF.name],
    DeviceType.S_RGB_LIGHT.name: [ActionType.V_RGB.name, ActionType.V_WATT.name],
    DeviceType.S_RGBW_LIGHT.name: [ActionType.V_RGBW.name, ActionType.V_WATT.name],
    DeviceType.S_COLOR_SENSOR.name: [ActionType.V_RGB.name],
    DeviceType.S_HVAC.name: [ActionType.V_HVAC_SETPOINT_COOL.name, ActionType.V_HVAC_SETPOINT_HEAT.name, ActionType.V_HVAC_FLOW_STATE.name, ActionType.V_HVAC_FLOW_MODE.name, ActionType.V_HVAC_SPEED.name, ActionType.V_TEMP.name, ActionType.V_STATUS.name],
    DeviceType.S_MULTIMETER.name: [ActionType.V_VOLTAGE.name, ActionType.V_CURRENT.name, ActionType.V_IMPEDANCE.name],
    DeviceType.S_SPRINKLER.name: [ActionType.V_STATUS.name, ActionType.V_TRIPPED.name],
    DeviceType.S_WATER_LEAK.name: [ActionType.V_TRIPPED.name, ActionType.V_ARMED.name],
    DeviceType.S_SOUND.name: [ActionType.V_LEVEL.name, ActionType.V_TRIPPED.name, ActionType.V_ARMED.name],
    DeviceType.S_VIBRATION.name: [ActionType.V_LEVEL.name, ActionType.V_TRIPPED.name, ActionType.V_ARMED.name],
    DeviceType.S_MOISTURE.name: [ActionType.V_LEVEL.name, ActionType.V_TRIPPED.name, ActionType.V_ARMED.name],
    DeviceType.S_INFO.name: [ActionType.V_TEXT.name],
    DeviceType.S_GAS.name: [ActionType.V_FLOW.name, ActionType.V_VOLUME.name],
    DeviceType.S_GPS.name: [ActionType.V_POSITION.name],
    DeviceType.S_WATER_QUALITY.name: [ActionType.V_TEMP.name, ActionType.V_PH.name, ActionType.V_ORP.name, ActionType.V_EC.name, ActionType.V_STATUS.name],
    DeviceType.S_FAN.name: [ActionType.V_TEMP.name, ActionType.V_PERCENTAGE.name, ActionType.V_DIRECTION.name, ActionType.V_STATUS.name]
}

def get_action_types(device_type):
    return device_action_dict[device_type] if device_type in device_action_dict else None

def obtain_action_types(device_type):
    values = get_action_types(device_type)
    if values is None:
        return {}
    else:
        return {value: (None, False) for value in values}
