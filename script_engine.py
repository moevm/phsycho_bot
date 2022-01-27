import copy
import json
import logging
import pytz
import datetime
from telegram import Update
from telegram.ext import CallbackContext
from db import init_user, get_survey_progress, init_survey_progress, get_user_answer
from keyboard import yes_no_keyboard


class Script:  # класс для хранения дерева
    def __init__(self, tree: dict):
        self.tree = tree

    def get_script(self, script_name):
        return self.tree[script_name]['script_body']


class Parser:  # класс для загрузки дерева из json
    def __init__(self, file_with_script: str):
        self.__data = {}
        self.__file_name = file_with_script

    def parse(self):
        with open(self.__file_name) as stream:
            self.__data = json.load(stream)
        return copy.deepcopy(self.__data)


class Step:  # класс для работы с текущим шагом
    def __init__(self, update, survey_progress, focus):
        self.update = update
        self.survey_progress = survey_progress
        self.step_info = Script(Parser("tree_example.json").parse()).get_script(focus)[survey_progress.survey_step]

    def processing_options(self):
        next_step = None
        for option in self.step_info['options']:
            if option['type'] == 'send_message':
                self.update.effective_user.send_message(text=option['text'],)
            elif option['type'] == 'get_user_answer':
                answer = get_user_answer(init_user(self.update.effective_user), self.step_info['script_name'],
                                         option['step'])
                self.update.effective_user.send_message(answer)
            elif option['type'] == 'inline_keyboard':
                self.update.effective_user.send_message(text=option['text'],
                                                        reply_markup=yes_no_keyboard())
            elif option['type'] == 'inline_answer' and self.update.callback_query is not None:
                if option['answer'] == self.update.callback_query.data:
                    if option['message']['type'] == 'text':
                        self.update.effective_user.send_message(text=option["message"]["text"])
                    elif option['message']['type'] == 'voice':
                        with open(option["message"]["source"], 'rb') as stream:
                            self.update.effective_user.send_voice(voice=stream)
                    elif option['message']['type'] == 'inline_keyboard':
                        self.update.effective_user.send_message(text=option["message"]["text"],
                                                                reply_markup=yes_no_keyboard())
                    next_step = option['next']

            elif option['type'] == 'send_voice':
                with open(option["source"], 'rb') as stream:
                    self.update.effective_user.send_voice(voice=stream)
        return next_step

    def execute(self) -> str:
        next = self.processing_options()
        if next is not None:
            self.survey_progress.survey_next = next
        self.survey_progress.time_send_question = pytz.utc.localize(datetime.datetime.utcnow())
        self.survey_progress.need_answer = self.step_info['need_answer']
        self.survey_progress.save()
        return self.step_info['state']


class Engine:  # класс движка
    def __init__(self, update: Update, context: CallbackContext):
        self.update = update
        self.user = init_user(self.update.effective_user)
        self.last_focus = self.user.focuses[-1]['focus']
        self.survey_progress = None

    def get_next_step(self) -> Step:
        self.survey_progress = get_survey_progress(self.user, self.last_focus)
        step_number = self.survey_progress.survey_step
        if self.update.callback_query is not None:
            self.update.callback_query.delete_message()
        if self.survey_progress.time_send_question != self.survey_progress.time_receive_answer:
            # обработка предыдущего шага
            if self.update.callback_query is not None:
                query = self.update.callback_query
                query.answer()
                self.survey_progress.user_answer = query.data
                self.survey_progress.time_receive_answer = query.message.date
            else:
                self.survey_progress.user_answer = self.update.message.text
                self.survey_progress.time_receive_answer = self.update.message.date
            self.survey_progress.save()
            step_number = self.survey_progress.survey_next
        # Генерация нового
        new_step_info = Script(Parser("tree_example.json").parse()).get_script(self.last_focus)[step_number]
        new_survey_progress = init_survey_progress(self.user, self.last_focus, self.update.update_id, step_number, new_step_info['next'])
        next_step = Step(self.update, new_survey_progress, self.last_focus)
        return next_step
