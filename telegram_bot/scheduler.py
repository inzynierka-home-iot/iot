def parse_payload_to_time(hours, minutes, days):
    hours = hours.split("=")[1]
    minutes = minutes.split("=")[1]
    days_variable = days.split("=")
    if len(days_variable) == 2:
        output = f"{minutes} {hours} * * {days_variable[1]}"
    else:
        output = f"{minutes} {hours} * * *"
    return output


def generate_new_schedule(home_id, node_id, device_id, payload):
    if home_id == "*" or node_id == "*" or device_id == "*":
        raise Exception("Flow can be set only to single device!")
    if "&" not in payload:
        if payload == "action=remove":
            return {
                "command": "remove",
                "name": home_id + "/" + node_id + "/" + device_id
            }

    action, params = payload.split("&", 1)
    action = action.split("=")[1]

    if action == "getTemp":
        hours, minutes, days = params.split("&")

        try:

            time = parse_payload_to_time(hours, minutes, days)
        except:
            raise Exception("Invalid data format")
        schedule = {
            "command": "add",
            "name": home_id + "/" + node_id + "/" + device_id,
            "expression": time,
            "payload": {
                "action": "getTemp",
                "nodeIn": f"nodeRED-out/{home_id}/{node_id}/{device_id}/status/?V_TEMP",
                "nodeOut": f"nodeRED-in/{home_id}/{node_id}/{device_id}"
            },
            "type": "json"
        }
    elif action == "maintain":
        try:
            location, node, device, temp = params.split("&")
            location = location.split("=")[1]
            node = node.split("=")[1]
            device = device.split("=")[1]
            temp = int(temp.split("=")[1])
        except:
            raise Exception("Invalid data format")
        schedule = {
            "command": "add",
            "name": home_id + "/" + node_id + "/" + device_id,
            "expression": "*/10 * * * * *",
            "payload": {
                "action": "maintainTemp",
                "tempNodeIn": f"nodeRED-out/{location}/{node}/{device}/status/?V_TEMP",
                "tempNodeOut": f"nodeRED-in/{location}/{node}/{device}",
                "device": f"{home_id}/{node_id}/{device_id}",
                "requestedTemp": temp
            },
            "type": "json"
        }
    elif action == "motionAlarm":
        try:
            location, node, device = params.split("&")
            location = location.split("=")[1]
            node = node.split("=")[1]
            device = device.split("=")[1]
        except:
            raise Exception("Invalid data format")
        schedule = {
            "command": "add",
            "name": home_id + "/" + node_id + "/" + device_id,
            "expression": "*/2 * * * * *",
            "payload": {
                "action": "motionAlarm",
                "nodeIn": f"nodeRED-out/{location}/{node}/{device}/status/?V_TRIPPED",
                "nodeOut": f"nodeRED-in/{location}/{node}/{device}",
                "device": f"{home_id}/{node_id}/{device_id}"
            },
            "type": "json"
        }
    elif action == "automaticSprinkler":
        try:
            params_listed= params.split("&")
            dict_params=dict()
            for param in params_listed:
                splited_param=param.split("=")
                dict_params[splited_param[0]]=splited_param[1]
        except:
            raise Exception("Invalid data format")
        schedule = {
            "command": "add",
            "name": home_id + "/" + node_id + "/" + device_id,
            "expression": "*/10 * * * * *",
            "payload": {
                "action": "automaticSprinkler",
                "hum" : {
                    "nodeIn": f"nodeRED-out/{dict_params['humLocation']}/{dict_params['humNodeId']}/{dict_params['humId']}/status/?V_HUM",
                    "nodeOut": f"nodeRED-in/{dict_params['humLocation']}/{dict_params['humNodeId']}/{dict_params['humId']}",
                },
                "hum_value":dict_params["V_HUM"],
                "light" : {
                    "nodeIn": f"nodeRED-out/{dict_params['lightLocation']}/{dict_params['lightNodeId']}/{dict_params['lightId']}/status/?V_LIGHT_LEVEL",
                    "nodeOut": f"nodeRED-in/{dict_params['lightLocation']}/{dict_params['lightNodeId']}/{dict_params['lightId']}",
                },
                "light_value":dict_params["V_LIGHT_LEVEL"],
                "device": f"{home_id}/{node_id}/{device_id}"
            },
            "type": "json"
        }
    else:
        return "unknown"
    return schedule


def generate_readable_scheduler(home_id, node_id, device_id, payload):
    params = payload.split("&")
    readable_schedule = dict()
    for param in params:
        key, value = param.split("=")
        readable_schedule[key] = value
    return readable_schedule
