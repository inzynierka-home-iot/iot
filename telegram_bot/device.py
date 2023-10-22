import json
import time
from datetime import datetime
from collections import deque

from device_action_mapper import obtain_action_types

class Device:

    def __init__(self, location, node_id, device_id, device_type, description):
        self.location = location
        self.node_id = node_id
        self.device_id = device_id
        self.device_type = device_type
        self.name = description
        self.values = obtain_action_types(device_type)
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
            'values': {k: v[0] for k, v in self.values.items()}
        }
        return json.dumps(value)

    def update_value(self, value_type, value):
        if value_type in self.values.keys():
            self.values[value_type] = (value, self.values[value_type][1])
        else:
            self.values[value_type] = (value, False)
        with open(f'sensor_data/{self.location}_{self.node_id}_{self.device_id}_{value_type}.txt', 'r') as f:
            buffer = deque(f.readlines(), maxlen=1000)
        buffer.append(json.dumps({'time': datetime.now().isoformat(), 'value': value}) + '\n')
        with open(f'sensor_data/{self.location}_{self.node_id}_{self.device_id}_{value_type}.txt', 'w') as f:
            f.writelines(buffer)

    def get_value(self, value_types=None):
        values = {k: v[0] for k, v in self.values.items()} if value_types is None else {k: v[0] for k, v in self.values.items() if k in value_types}
        return json.dumps(values) if len(values) > 0 else {"status": False}

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