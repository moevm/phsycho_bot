from pyrogram import Client


def get_app_info():
    with open('app_variables.txt', encoding="utf-8") as f:
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
    app = Client("my_account", api_id, api_hash)
    return app, username

print(get_app_info())