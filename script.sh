#!/bin/bash

# Check if config file exists, exit if not
if [ ! -f ./config.json ]
then
    echo "Configuration file 'config.json' not found, please add it and set it up." >&2
    exit 1
fi

# With this, if any command gives error, whole script stops
set -e

# Our logs will go to the standard output
exec 3>&1

# Debug mode
DEBUG_MODE=$(cat config.json | jq -r '.debug')

# If silence output is on, we will neglect any logs coming to the 
# standard output and make our logs redirect to a different output
SILENT_OUTPUT=$(cat config.json | jq -r '.silentOutput')
if [ $SILENT_OUTPUT == 'true' ] && [ $DEBUG_MODE == 'false' ]
then
    exec 1>/dev/null
fi

# Initialize status related variables
STATUS_MESSAGE="Test"
STATUS_EXPIRY_DATE=$(( $(date +%s -d "today 23:59") ))
STATUS_EMOJI=$(cat config.json | jq -r '.statusEmoji')

# Loop through the api tokens provided in the config
TOKEN_NUMBER=1
cat config.json | jq -r '.slackApiTokens[]' | while read SLACK_API_TOKEN ; do
    echo "Configuring the ${TOKEN_NUMBER}. workspace..." >&3

    # Send the request to slack
    SLACK_RESPONSE=$(curl -sS 'https://slack.com/api/users.profile.set' \
        --header "Authorization: Bearer ${SLACK_API_TOKEN}" \
        --header 'Content-Type: application/json' \
        --data-raw "{
        \"profile\": {
                \"status_text\": \"${STATUS_MESSAGE}\",
                \"status_emoji\": \"${STATUS_EMOJI}\",
                \"status_expiration\": $STATUS_EXPIRY_DATE
            }
        }" | jq -r '.')

    # Log response if necessary
    if [ $SILENT_OUTPUT == 'false' ]
    then
        echo $SLACK_RESPONSE
    fi

    # Handle error if it's present
    SLACK_RESPONSE_STATUS=$(echo $SLACK_RESPONSE | jq -r '.ok')
    if [ $SLACK_RESPONSE_STATUS == 'false' ]
    then
        SLACK_RESPONSE_ERROR=$(echo $SLACK_RESPONSE | jq -r '.error')
        echo "Error on setting slack status: ${SLACK_RESPONSE_ERROR}" >&2
    else
        echo "Done" >&3
    fi

    TOKEN_NUMBER=$(($TOKEN_NUMBER+1))
done
