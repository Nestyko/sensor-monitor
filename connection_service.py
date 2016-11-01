from config import load_config
import requests

def is_server_up():
    data = load_config()
    url = data['base_url']
    r = requests.get(url)
    return r.status_code == 200