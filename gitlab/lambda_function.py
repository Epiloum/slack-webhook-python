import json
import os
import requests

SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")
SLACK_USERNAME ='GitLab 알리미' 
SLACK_ICON = ':gitlab:'

def lambda_handler(event, context):
    try:
        # Assuming the incoming event is a GitLab webhook payload
        data = json.loads(event['body'])

        # Get the object_kind from the payload
        object_kind = data.get('object_kind', '')

        # Generate message based on object_kind
        message = generate_message(object_kind, data)

        # Send message to Slack
        send_slack_message(message)

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Webhook received successfully'})
        }

    except Exception as e:
        print(f"Error processing webhook: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal Server Error'})
        }

def generate_message(object_kind, data):
    if object_kind == 'push':
        repository = data['repository']['name']
        branch = extract_branch_name(data['ref'])
        username = data['user_name']
        url = data['repository']['homepage']

        description = data['commits'][0]['message'] if 'commits' in data and data['commits'] else "No commit message available"
        # Remove newline characters from the commit message
        description = description.replace('\n', ' ')

        return f"【 *Push* 】 {repository}\n> *{username}* `{branch}` \n>{description}\n>\n><{url}|Details...>"

    elif object_kind == 'merge_request':
        action = data['object_attributes']['action']
        repository = data['repository']['name']
        source_branch = data['object_attributes']['source_branch']
        target_branch = data['object_attributes']['target_branch']
        username = data['user']['username']
        url = data['object_attributes']['url']
        description = data['object_attributes']['description']

        return f"【 *Merge Request* / {action} 】 {repository}\n> *{username}* `{source_branch}` → `{target_branch}` \n>{description}\n>\n><{url}|Details...>"

    else:
        return f"Unhandled object_kind: {object_kind}"

def extract_branch_name(ref):
    return "/".join(ref.split('/')[2:])

def send_slack_message(message):
    payload = {'text': f':gitlab: {message}', 'username':SLACK_USERNAME, 'icon_emoji':SLACK_ICON}

    try:
        response = requests.post(SLACK_WEBHOOK_URL, data=json.dumps(payload), headers={'Content-Type': 'application/json'})
        response.raise_for_status()
        print("Slack message sent successfully")
    except requests.exceptions.RequestException as e:
        print(f"Error sending Slack message: {e}")