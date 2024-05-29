from os import getenv

DEBUG_MODE = getenv('DEBUG_MODE')
LANGUAGE = getenv('LANGUAGE')
SAMPLE_RATE = getenv('SAMPLE_RATE')
SPEAKER = getenv('SPEAKER')
ASR_ENGINE = getenv('ASR_ENGINE')
ASR_MODEL = getenv('ASR_MODEL')
TOKEN = getenv('TELEGRAM_TOKEN')
DELAY = int(getenv('DELAY'))

DEBUG_ON, DEBUG_OFF = "true", "false"
