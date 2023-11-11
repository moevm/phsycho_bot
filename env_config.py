from os import getenv

ADMIN = getenv('ADMIN')

DEBUG_MODE = getenv('DEBUG_MODE')
MODE = getenv('MODE')  # delete
DIALOG_MODE = getenv('DIALOG_MODE')  # delete
LANGUAGE = getenv('LANGUAGE')
SAMPLE_RATE = getenv('SAMPLE_RATE')
SPEAKER = getenv('SPEAKER')
ASR_ENGINE = getenv('ASR_ENGINE')
ASR_MODEL = getenv('ASR_MODEL')

TEXT_MODE, VOICE_MODE, DEBUG_ON, DEBUG_OFF = "text", "voice", "true", "false"
