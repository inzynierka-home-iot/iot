import json
import time
from datetime import datetime
from collections import deque

from device_action_mapper import obtain_action_types

class Device:

    def __init__(self, location, node_id, device_id, device_type, description, schedule=dict()):
        self.location = location
        self.node_id = node_id
        self.device_id = device_id
        self.device_type = device_type
        self.name = description
        self.values = obtain_action_types(device_type)
        self.schedule = schedule
        self.last_seen = time.time()

    def __eq__(self, other):
        return self.location == other.location and self.node_id == other.node_id and self.device_id == other.device_id

    def __str__(self):
        value = {
            'location': self.location,
            'nodeId': self.node_id,
            'id': self.device_id,
            'type': self.device_type,
            'name': self.name,
            'schedule': self.schedule,
            'values': {k: v[0] for k, v in self.values.items()}
        }
        return json.dumps(value)

    def __repr__(self):
        value = {
            'location': self.location,
            'nodeId': self.node_id,
            'id': self.device_id,
            'type': self.device_type,
            'name': self.name,
            'schedule': self.schedule,
            'values': {k: v[0] for k, v in self.values.items()}
        }
        return json.dumps(value)

    def update_info(self, location, node_id, device_id, device_type, description):
        self.location = location
        self.node_id = node_id
        self.device_id = device_id
        self.device_type = device_type
        self.description = description

    def update_value(self, value_type, value):
        if value_type in self.values.keys():
            self.values[value_type] = (value, self.values[value_type][1])
        else:
            self.values[value_type] = (value, False)

    def save_values(self):
        for value_type, value in self.values.items():
            try:
                with open(f'sensor_data/{self.location}_{self.node_id}_{self.device_id}_{value_type}.txt', 'r') as f:
                    buffer = deque(f.readlines(), maxlen=1000)
                buffer.append(json.dumps({'time': datetime.now().isoformat(), 'value': value[0]}) + '\n')
            except:
                buffer = deque()
                buffer.append(json.dumps({'time': datetime.now().isoformat(), 'value': value[0]}) + '\n')
            with open(f'sensor_data/{self.location}_{self.node_id}_{self.device_id}_{value_type}.txt', 'w') as f:
                f.writelines(buffer)

    def update_schedule(self, schedule):
        self.schedule = schedule

    def get_dump_values(self, value_types):
        values = {k: v[0] for k, v in self.values.items()} if len(value_types) == 0 else {k: v[0] for k, v in self.values.items() if k in value_types}
        return json.dumps(values) if len(values) > 0 else {"status": False}

    def get_value(self, value_type):
        if value_type in self.values.keys():
            if self.values[value_type] is not None:
                return self.values[value_type][0]
        return {"status": False}

    def get_historical_values(self, value_type):
        with open(f'sensor_data/{self.location}_{self.node_id}_{self.device_id}_{value_type}.txt', 'r') as f:
            values_list = []
            for line in (f.readlines() [-15:]):
                values_list.append(json.loads(line)['value'])

        values = {value_type: values_list}
        return json.dumps(values) if value_type in self.values.keys() else {"status": False}

    def subscribe(self, value_type=None):
        if value_type is None:
            for value_type in self.values:
                self.values[value_type] = (self.values[value_type][0], True)
        else:
            self.values[value_type] = (self.values[value_type][0], True)


    def unsubscribe(self, value_type=None):
        if value_type is None:
            for value_type in self.values:
                self.values[value_type] = (self.values[value_type][0], False)
        else:
            self.values[value_type] = (self.values[value_type][0], False)

    def update_last_seen(self):
        self.last_seen = time.time()
