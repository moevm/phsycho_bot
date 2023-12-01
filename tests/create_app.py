from pyrogram import Client


def get_app_info():
    with open('app_variables.txt', encoding="utf-8") as f:
        app_variables = f.read().split('\n')
    return app_variables


api_id, api_hash, username = get_app_info()
app = Client("my_account", api_id, api_hash)
