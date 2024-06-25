from time import sleep
import pyrogram
import pytest
from create_app import create_app


@pytest.fixture(scope='module')
def app_and_username():
    app, username = create_app()
    app.start()
    yield app, username
    app.stop()


def test_start_command(app_and_username):
    app, username = app_and_username
    msg = app.send_message(username, '/start')
    sleep(1)
    msg = app.get_messages(username, msg.id + 1)
    assert msg.text == 'Здравствуйте! Я бот-психолог. Как можно обращаться к вам?'
    msg = app.send_message(username, 'User')
    sleep(1)
    msg = app.get_messages(username, msg.id + 1)
    assert msg.text == 'Приятно познакомиться, User! Удобно будет на ты или лучше на Вы?'
    msg.click(0)
    sleep(1)
    msg = app.get_messages(username, msg.id + 1)
    msg.click(0)
    sleep(1)
    msg = app.get_messages(username, msg.id + 1)
    assert msg.text == 'Спасибо! Ты можешь изменить обращение в любой момент командой /change_pronoun'
    sleep(1)
    msg = app.get_messages(username, msg.id + 1)
    assert msg.text == 'Спасибо! Ты можешь изменить способ общения в любой момент командой /change_mode'
    sleep(1)
    msg = app.get_messages(username, msg.id + 1)
    assert msg.text == ('Сейчас немного расскажу, как будет устроено наше взаимодействие. Данное приложение '
                        'построено на базе психологической методики под названием "когнитивно-поведенческая '
                        'терапия" или КПТ. Эта методика является одним из современных направлений в психологии и '
                        'имеет множество клинических подтверждений эффективности . Я буду выполнять с тобой '
                        'несколько упражнений в зависимости от твоего запроса, помогу отследить твое состояние, '
                        'а также мысли и чувства. Есть ли какие-то вопросы?')

    msg.click(0)
    sleep(1)
    menu_msg = app.get_messages(username, msg.id + 1)
    assert menu_msg.text == ('Если тебе интересно, то подробнее о методе можно прочитать в книгах Девид Бернса '
                             '"Терапия Настроения" и Роберта Лихи "Свобода от тревоги".')

    msg.click(1)
    sleep(1)
    menu_msg = app.get_messages(username, menu_msg.id + 1)
    assert menu_msg.text == ('Методы психотерапии действуют на всех индивидуально и мне сложно прогнозировать '
                             'эффективность, однако, согласно исследованиям эффект может наблюдаются уже через '
                             'месяц регулярных занятий')

    msg.click(2)
    sleep(1)
    menu_msg = app.get_messages(username, menu_msg.id + 1)
    assert menu_msg.text == 'Для того, чтобы методы'

    msg.click(3)
    sleep(1)
    menu_msg = app.get_messages(username, menu_msg.id + 1)
    assert menu_msg.text == ('Предлагаемые мной упражнения и практики не являются глубинной работой и играют роль '
                             'как вспомогательное средство. Я не рекомендую данных метод для случаев, '
                             'когда запрос очень тяжелый для тебя')

    msg.click(4)
    sleep(1)
    menu_msg = app.get_messages(username, menu_msg.id + 1)
    assert menu_msg.text == 'Я передам твой вопрос нашему психологу-консультанту и в ближайшее время пришлю ответ.'

    msg.click(5)
    sleep(1)
    menu_msg = app.get_messages(username, menu_msg.id + 1)
    assert menu_msg.text == ('Если у тебя нет вопросов, мы можем начать. Расскажи, пожалуйста, максимально '
                             'подробно, почему ты решил_а обратиться ко мне сегодня, о чем бы тебе хотелось '
                             'поговорить? Наш разговор совершенно конфиденциален')

    msg = app.send_message(username, 'семья')
    sleep(1)
    msg = app.get_messages(username, msg.id + 1)
    assert msg.text == 'В какое время тебе удобно подводить итоги дня?'
    msg.click(0)
    sleep(1)
    msg = app.get_messages(username, msg.id + 1)
    assert msg.text == 'Ты выбрал 18:00 - 19:00 в качестве времени для рассылки. Спасибо!'
    msg = app.get_messages(username, msg.id + 1)
    assert msg.text == ('Подведение итогов дня поможет исследовать определенные сложности и паттерны твоего '
                        'поведения. Каждую неделю можно выбирать разные фокусы или один и тот же. Выбрать фокус '
                        'этой недели:')
    msg.click(0)
    sleep(1)
    msg = app.get_messages(username, msg.id + 1)
    assert msg.text == ('Ты выбрал фокусом этой недели работу с усталостью. Для начала вспомни, какие события или '
                        'действия наполняют тебя ресурсом, дает прилив энергии и сил?')


def test_change_pronoun(app_and_username):
    app, username = app_and_username
    msg = app.send_message(username, '/change_pronoun')
    sleep(1)
    msg = app.get_messages(username, msg.id + 1)
    assert (msg.text == 'Режим общения изменен. Текущий режим: общение на "Вы"'
            or msg.text == 'Режим общения изменен. Текущий режим: общение на "Ты"')

    pronoun1 = msg.text.split()[-1]
    msg = app.send_message(username, '/change_pronoun')
    sleep(1)
    msg = app.get_messages(username, msg.id + 1)
    pronoun2 = msg.text.split()[-1]
    assert (pronoun1 != pronoun2)


def test_change_mode(app_and_username):
    app, username = app_and_username
    msg = app.send_message(username, '/change_mode')
    sleep(10)
    msg = app.get_messages(username, msg.id + 1)
    if msg.text:
        msg = app.send_message(username, '/change_mode')
        sleep(10)
        msg = app.get_messages(username, msg.id + 1)
    assert msg.media == pyrogram.enums.MessageMediaType.VOICE
