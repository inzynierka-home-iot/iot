class Device:

    def __init__(self, home_id, node_id, device_id, device_type, description):
        self.home_id = home_id
        self.node_id = node_id
        self.device_id = device_id
        self.device_type = device_type
        self.description = description
        self.values = {}


    def __str__(self):
        return f'{self.home_id}/{self.node_id}/{self.device_id}/{self.device_type}/{self.description}'

    def __repr__(self):
        return f'{self.home_id}/{self.node_id}/{self.device_id}/{self.device_type}/{self.description}'

    def update_value(self, value_type, value):
        if value_type in self.values.keys():
            self.values[value_type] = (value, self.values[value_type][1])
        else:
            self.values[value_type] = (value, False)

    def get_value(self, value_type=None):
        if value_type is None:
            response = ''
            for value_type in self.values:
                response += f', {value_type}: {self.values[value_type][0]}'
            return response

        return f', {value_type}: {self.values[value_type][0]}' if value_type in self.values else None


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