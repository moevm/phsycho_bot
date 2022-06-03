for i in {1..5}
do
  mongo phsycho_bot_speed_test --eval "db.dropDatabase()"
  python3 test_speed.py >> results.txt
done
