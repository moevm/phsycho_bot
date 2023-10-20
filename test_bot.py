from time import sleep
from pyrogram import Client


def verify_response(expected_value: str, received_value: str):
    if not received_value.startswith(expected_value):
        print("It's not what I expected.")
        print(f"\tExpected: {expected_value}")
        print(f"\tReceived: {received_value}")


def delay(seconds=2):
    sleep(seconds)


def run_test(app, filename):
    with open(filename, encoding="utf-8") as f:
        test_configs = [line.split('|') for line in f.read().split('\n')]

    msg = None
    for input_value, expected_value in test_configs:
        msg = app.send_message(username, input_value)
        delay(1)
        msg = app.get_messages(username, msg.id + 1)
        verify_response(expected_value, msg.text)
        delay()


api_id = 24165427
api_hash = "2c74ae389b90a8d11320ea3e61e3a494"
username = "silero_demo_bot"
with Client("my_account", api_id, api_hash) as app:
    run_test(app, 'test.csv')
