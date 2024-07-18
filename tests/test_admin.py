from time import sleep
import pytest
from create_app import create_app


@pytest.fixture(scope='module')
def app_and_username():
    app, username = create_app()
    app.start()
    yield app, username
    app.stop()


def test_add_admin(app_and_username):
    app, username = app_and_username
    msg = app.send_message(username, '/add_admin 1234567')
    sleep(1)
    msg = app.get_messages(username, msg.id + 1)
    assert msg.text == 'Выданы права администратора пользователю с id: 1234567'


def test_update_info(app_and_username):
    app, username = app_and_username
    msg = app.send_message(username, '/update_info')
    sleep(1)
    msg = app.get_messages(username, msg.id + 1)
    assert msg.text == 'Информация успешно обновлена.'


def test_get_and_answer_support_questions(app_and_username):
    app, username = app_and_username
    msg = app.send_message(username, '/get_support_questions')
    sleep(1)
    msg = app.get_messages(username, msg.id + 1)
    assert msg.text.startswith('Всего страниц:') is True
    msg = app.get_messages(username, msg.id + 1)
    if msg:
        questions_info = msg.text
        question_id = questions_info.split()[1]
        msg = app.send_message(username, '/answer_support_question')
        sleep(1)
        msg = app.get_messages(username, msg.id + 1)
        assert msg.text == 'Введите идентификатор вопроса:'
        msg = app.send_message(username, question_id)
        sleep(1)
        msg = app.get_messages(username, msg.id + 1)
        assert msg.text == 'Выбранный вопрос: "Как долго ждать ответ?"'
        msg = app.send_message(username, 'Не долго')
        sleep(1)
        msg = app.get_messages(username, msg.id + 1)
        assert msg.text == 'Ответ успешно создан!'
