from os import getenv

ADMIN = int(getenv('ADMIN'))

DEBUG_MODE = getenv('DEBUG_MODE')
MODE = getenv('MODE')
DIALOG_MODE = getenv('DIALOG_MODE')
LANGUAGE = getenv('LANGUAGE')
SAMPLE_RATE = getenv('SAMPLE_RATE')
SPEAKER = getenv('SPEAKER')

TEXT_MODE, VOICE_MODE, DEBUG_ON, DEBUG_OFF = "text", "voice", "true", "false"
