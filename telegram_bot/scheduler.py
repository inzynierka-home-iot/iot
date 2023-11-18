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
                "nodeIn": f"{home_id}-in/{node_id}/{device_id}/2/0/0",
                "nodeOut": f"{home_id}-out/{node_id}/{device_id}/1/0/0"
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
                "tempNodeIn": f"{location}-in/{node}/{device}/2/0/0",
                "tempNodeOut": f"{location}-out/{node}/{device}/1/0/0",
                "device": f"{home_id}/{node_id}/{device_id}",
                "requestedTemp": temp
            },
            "type": "json"
        }
    else:
        return "unknown"
    return schedule


def generate_redable_scheduler(home_id, node_id, device_id, payload):
    params = payload.split("&")
    readable_schedule = dict()
    for param in params:
        key, value = param.split("=")
        readable_schedule[key] = value
    return readable_schedule
