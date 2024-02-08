#! /bin/bash

pytest test.py
echo Pytest exited $?
#pytest test.py -s --disable-warnings