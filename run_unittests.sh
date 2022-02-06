#!/bin/bash

DB_ADDRESS='mongodb://127.0.0.1:27017/test_db'

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
python3 test_script_engine.py ${DB_ADDRESS} -v 2>&1 | tee unittest_logs.txt
exit_code="${PIPESTATUS[0]}"
#echo $?