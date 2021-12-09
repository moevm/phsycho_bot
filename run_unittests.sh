#!/bin/bash

# drop test db
mongo test_db --eval "db.dropDatabase()"

# import test db
mongoimport --db test_db --collection user --file test_user.json
mongoimport --db test_db --collection survey_progress --file test_survey_progress.json
mongoimport --db test_db --collection schedule> --file test_schedule.json

# run tests
python3 test_script_engine.py -v 2>&1 | tee unittest_logs.txt