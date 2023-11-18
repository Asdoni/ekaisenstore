import json

class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.load_config()
        return cls._instance

    def load_config(self):
        with open('config.json', 'r') as config_file:
            self.config_data = json.load(config_file)
            self.token = self.config_data['token']
