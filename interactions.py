import os
import json
import requests
from pathlib import Path
import slack
from dotenv import load_dotenv
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter

# Load environment variables
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# File to store user preferences
USER_PREFERENCES_FILE = 'user_preferences.json'

# Initialize Flask and Slack clients
app = Flask(__name__)
client = slack.WebClient(token=os.environ['SLACK_TOKEN'])
BOT_ID = client.api_call("auth.test")['user_id']
slack_event_adapter = SlackEventAdapter(os.environ['SIGNING_SECRET'], '/slack/events', app)

# ------------------ Google Bard ------------------ #

Google_API_KEY = os.environ['Google_API_KEY']
Google_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={Google_API_KEY}"

def translate_text(user_text, sender_id, channel_id):
    preferences = load_user_preferences()
    user_details = preferences.get(sender_id,{})
    sender_language, username = user_details['language'], user_details['username']

    #sender_language = preferences.get(sender_id, {}).get("language", "English")

    for user_id, info in preferences.items():
        if user_id == sender_id:
            continue  # Don't translate for sender

        target_language = info.get("language", "English")

        if target_language == sender_language:
            continue  # Same language, no need to translate
    


        data = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": f"Translate the following sentence from {sender_language} to {target_language}. Respond only with the translated sentence and nothing else:\n\n{user_text}"
                        }
                    ]
                }
            ]
        }


        
        try:
            response = requests.post(Google_API_URL, json=data)
            output = response.json()
            translated_text = output.get("candidates", [])[0]["content"]["parts"][0]["text"]

        except Exception as e:
            translated_text = f"⚠️ Failed to translate: {e}"
            print(f"Error: {response.text}")

        # Send to the target user
        client.chat_postEphemeral(
            channel=channel_id,
            user=user_id,
            text=f"Translated message from @{username}:\n\n {translated_text}"
        )




# ------------------ User Preferences Handling ------------------ #

def load_user_preferences():
    try:
        if os.path.exists(USER_PREFERENCES_FILE):
            with open(USER_PREFERENCES_FILE, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"Error loading preferences: {e}")
        return {}

def save_user_preferences(preferences):
    try:
        with open(USER_PREFERENCES_FILE, 'w') as f:
            json.dump(preferences, f, indent=2)
    except Exception as e:
        print(f"Error saving preferences: {e}")

def is_first_time_user(user_id):
    preferences = load_user_preferences()
    return user_id not in preferences

def is_waiting_for_language(user_id):
    preferences = load_user_preferences()
    return preferences.get(user_id, {}).get('waiting_for_language', False)

def ask_for_language_preference(channel_id, user_id):
    preferences = load_user_preferences()
    preferences[user_id] = {
        'username': None,
        'language': None,
        'waiting_for_language': True
    }
    save_user_preferences(preferences)

    # Use a block message for interactive language selection
    client.chat_postEphemeral(
        channel=channel_id,
        user=user_id,
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "👋 Welcome! Please select your *preferred language*:"
                },
                "accessory": {
                    "type": "static_select",
                    "action_id": "select_language",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Choose language"
                    },
                    "options": [
                        {"text": {"type": "plain_text", "text": "English"}, "value": "English"},
                        {"text": {"type": "plain_text", "text": "Spanish"}, "value": "Spanish"},
                        {"text": {"type": "plain_text", "text": "German"}, "value": "German"},
                        {"text": {"type": "plain_text", "text": "Portuguese"}, "value": "Portuguese"},
                        {"text": {"type": "plain_text", "text": "Hindi"}, "value": "Hindi"},
                        {"text": {"type": "plain_text", "text": "Telugu"}, "value": "Telugu"}
                    ]
                }
            }
        ]
    )


def save_language_preference(user_name, user_id, language):
    preferences = load_user_preferences()
    preferences[user_id] = {
        "username" : user_name,
        'language': language,
        'waiting_for_language': False
    }
    save_user_preferences(preferences)
    print(f"Saved language preference for {user_id}: {language}")

def get_preferred_language(user_id):
    preferences = load_user_preferences()
    return preferences.get(user_id, {}).get('language', 'English')

# ------------------ Message Event Handling ------------------ #

@slack_event_adapter.on("message")
def handle_message(payload):
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    user_text = event.get('text')

    if user_id is None or user_id == BOT_ID:
        return

    if is_first_time_user(user_id):
        ask_for_language_preference(channel_id, user_id)
        return

    if is_waiting_for_language(user_id):
        client.chat_postEphemeral(
            channel=channel_id,
            user=user_id,
            text="Please use the dropdown menu to select your preferred language."
        )
        return
    
    translate_text(user_text, user_id, channel_id)

# ------------------ Interactive Component Endpoint ------------------ #

@app.route('/slack/interactive', methods=['POST'])
def interactive_endpoint():
    try:
        payload = json.loads(request.form['payload'])
        # print(f"Interactive payload received: {payload}")

        if payload['type'] == 'block_actions':
            action = payload['actions'][0]

            if action['action_id'] == 'select_language':
                
                user_id = payload['user']['id']
                user_name = payload['user']['username']
                selected_language = action['selected_option']['value']
                channel_id = payload['channel']['id']

                save_language_preference(user_name, user_id, selected_language)
                
                client.chat_postEphemeral(
                    channel=channel_id,
                    user=user_id,
                    text=f"Perfect! I've saved *{selected_language}* as your preferred language. 🎉"
                )

        return Response(status=200)

    except Exception as error:
        print(f"Error handling interactive component: {error}")
        return Response(status=500)


# ------------------ Start the Flask App ------------------ #

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 1000)), debug=True)
