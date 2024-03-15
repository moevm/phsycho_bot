#! /bin/bash

# install dependences
pip install -r src/requirements.txt
pip install -r emotional_speech_recognizing/requirements.txt
pip install -r silero_demo/requirements.txt

# install pylint (for checking)
pip install pylint

# install black (for autofix)
pip install black
