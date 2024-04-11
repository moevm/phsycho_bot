#! /bin/bash

# WORKDIR
cd ..

pipreqs --savepath src/reqs-check.txt --mode no-pin src/
python requirements_check.py src/requirements.txt src/reqs-check.txt