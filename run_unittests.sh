#!/bin/bash

# drop test db
mongo test_db --eval "db.dropDatabase()"

# import test db
mongoimport --db test_db --collection user --file test_user.json
if [ $? -gt 0 ]; then
    echo 'Error occured during importing collection "User"'
    exit 1
fi
mongoimport --db test_db --collection survey_progress --file test_survey_progress.json
if [ $? -gt 0 ]; then
    echo 'Error occured during importing collection "Survey progress"'
    exit 1
fi
mongoimport --db test_db --collection schedule> --file test_schedule.json
if [ $? -gt 0 ]; then
    echo 'Error occured during importing collection "Schedule"'
    exit 1
fi


# run tests
python3 test_script_engine.py -v 2>&1 | tee unittest_logs.txt