RESULTS_FILE=results.txt
#REPEAT_EXPERIMENT=1
USERS_NUMBER=1000

rm $RESULTS_FILE
for i in {1..1}
do
  mongo phsycho_bot_speed_test --eval "db.dropDatabase()"
  result= python3 test_speed.py $USERS_NUMBER -v >> $RESULTS_FILE
done
python3 process_results.py