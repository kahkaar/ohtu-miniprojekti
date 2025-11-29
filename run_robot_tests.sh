#!/bin/bash

echo "Running story tests"

# Creating and setting up the database
poetry run python src/db_helper.py

echo "Database setup completed"

# Run Flask server in the background
poetry run python3 src/index.py &

echo "Started Flask server"

# Wait until the Flask server is ready to accept requests
while [ "$(curl -s -o /dev/null -w ''%{http_code}'' localhost:5001)" != "200" ];
  do sleep 1;
done

echo "Flask server is ready"

# Run Robot Framework tests with HEADLESS variable set to true
poetry run robot --variable HEADLESS:true src/story_tests

status=$?

# Kill the Flask server running on port 5001
kill $(lsof -t -i:5001)

exit $status
