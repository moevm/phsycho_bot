import unittest
from unittest import mock
from json.decoder import JSONDecodeError
import sys
from telegram import Update
import pytz
import datetime

from db import User, SurveyProgress, init_user, init_survey_progress
from script_engine import Script, Parser, Step
from pymodm import connect


class TestScript(unittest.TestCase):

    def test_get_script(self):
        self.assertEqual(Script({'f_tired': {'script_body': [{'script_name': 'f_tired', 'options':
            [{'type': 'send_message', 'text': 'message'}]}, {'script_name': 'f_tired',
                                                             'id': 'tired_0.1'}]}}).get_script('f_tired'), [
                             {'script_name': 'f_tired', 'options': [{'type': 'send_message', 'text': 'message'}]},
                             {'script_name': 'f_tired', 'id': 'tired_0.1'}])
        self.assertRaises(KeyError, Script({'f_tired': {'script_body': [{'script_name': 'f_tired', 'options':
            [{'type': 'send_message', 'text': 'message'}]}, {'script_name': 'f_tired',
                                                             'id': 'tired_0.1'}]}}).get_script('ff_tired'))


class TestParser(unittest.TestCase):

    def test_parse(self):
        self.assertEqual(Parser("test_tree.json").parse(),
                         {'f_tired': {'script_body': [{'script_name': 'f_tired', 'options':
                             [{'type': 'send_message', 'text': 'message'}]},
                                                      {'script_name': 'f_tired', 'id': 'tired_0.1'}]}})
        self.assertRaises(FileNotFoundError, Parser("test_treee.json").parse())
        self.assertRaises(JSONDecodeError, Parser("test_broken_tree.json").parse())


class TestStep(unittest.TestCase):

    @mock.patch('telegram.Update')
    @mock.patch('telegram.User')
    def test_processing_options(self, MockUser, MockUpdate):
        update = MockUpdate()
        update.effective_user = MockUser()
        update.effective_user.send_message.return_value = []
        update.callback_query.data = 'r_yes'
        user = init_user(User(**{'id': 681004065}))
        focus = 'f_self-doubt'
        survey_progress = init_survey_progress(user, focus=focus, survey_step=4)
        step = Step(update, survey_progress, focus)
        self.assertEqual(step.processing_options(), 3)

    @mock.patch('telegram.Update')
    @mock.patch('telegram.User')
    def test_execute(self, MockUser, MockUpdate):
        update = MockUpdate()
        update.effective_user = MockUser()
        update.effective_user.send_message.return_value = []
        user = init_user(User(**{'id': 681004065}))
        focus = 'f_tired'
        survey_progress = init_survey_progress(user, focus=focus, survey_step=0)
        step = Step(update, survey_progress, focus)
        self.assertEqual(step.execute(), "TYPING")


if __name__ == '__main__':
    db_address = sys.argv[1]
    connect(db_address)
    res = unittest.main(argv=['first-arg-is-ignored'], exit=False)
    sys.exit(int(not res.result.wasSuccessful()))
