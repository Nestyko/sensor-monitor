import json

thing_config_path = 'thing.config.json'
thing_data_path = 'thing.data.json'

def load_config():
    with open(thing_config_path) as conf_file:
        return json.load(conf_file)

def save_data(jwt, user_id):
    data = load_config()
    with open(thing_config_path, mode='w') as conf_file:
        data['jwt'] = jwt
        data['user_id'] = user_id
        json.dump(data, conf_file, indent=4, ensure_ascii=False)

def load_thing():
    with open(thing_data_path) as conf_file:
        return json.load(conf_file)

def update_thing(new_thing):
    with open(thing_data_path, mode='w') as conf_file:
        json.dump(new_thing, conf_file, indent=4, ensure_ascii=False)
