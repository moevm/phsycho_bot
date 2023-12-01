from time import sleep
from create_app import app, username


def test_start_command():
    with app:
        msg = app.send_message(username, '/start')
        sleep(1)
        msg = app.get_messages(username, msg.id + 1)
        assert msg.text == 'Привет! Я бот, который поможет тебе отрефлексировать твое настроение'
