from os import getenv

DEBUG_MODE = getenv('DEBUG_MODE')
LANGUAGE = getenv('LANGUAGE')
SAMPLE_RATE = getenv('SAMPLE_RATE')
SPEAKER = getenv('SPEAKER')

DEBUG_ON, DEBUG_OFF = "true", "false"
