import os
from pyrogram import Client


def get_app_info():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_variables_path = os.path.join(script_dir, 'app_variables.txt')

    with open(app_variables_path, encoding="utf-8") as f:
        lines = f.readlines()

    api_id, api_hash, username = None, None, None

    for line in lines:
        key, value = line.strip().split('=')
        if key == 'api_id':
            api_id = value
        elif key == 'api_hash':
            api_hash = value
        elif key == 'username':
            username = value
    return api_id, api_hash, username


def create_app():
    api_id, api_hash, username = get_app_info()
    app = Client("my_account", api_id, api_hash, workdir="./", in_memory=True)
    return app, username
