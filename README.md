# Slack Translation Bot 🌍

A Slack bot that provides real-time message translation between multiple languages using Google's Gemini AI API.

## Features ✨

- **Real-time Translation**: Automatically translates messages between users with different language preferences
- **Multi-language Support**: English, Spanish, German, Portuguese, Hindi, and Telugu
- **Interactive Setup**: Easy language selection using Slack dropdown menus
- **Private Translations**: Messages sent as ephemeral (private) messages

## Prerequisites 📋

- Python 3.7+
- Slack workspace with admin permissions
- Google Cloud Platform account with Gemini API access
- ngrok for local development

## Quick Setup 🚀

### 1. Install Dependencies
```bash
git clone <your-repository-url>
cd Slack_bot
pip install -r requirements.txt
```

### 2. Slack App Setup
1. Create a Slack App at [api.slack.com](https://api.slack.com/apps)
2. **OAuth & Permissions** - Add Bot Token Scopes:
   - `chat:write`, `chat:write.public`, `channels:read`, `groups:read`, `im:read`, `mpim:read`, `users:read`
3. **Event Subscriptions** - Enable and set URL to `https://your-domain.ngrok.io/slack/events`
   - Add Bot Events: `message.channels`, `message.groups`, `message.im`, `message.mpim`
4. **Interactivity** - Enable and set URL to `https://your-domain.ngrok.io/slack/interactive`
5. Install app to workspace and copy Bot Token + Signing Secret

### 3. Google Gemini API
1. Create project at [Google AI Studio](https://aistudio.google.com/)
2. Enable "Generative Language API"
3. Create API key

### 4. Environment Setup
Create `.env` file:
```env
SLACK_TOKEN=xoxb-your-slack-bot-token
SIGNING_SECRET=your-slack-signing-secret
Google_API_KEY=your-google-gemini-api-key
PORT=1000
```

### 5. Run the Bot
```bash
# Terminal 1
ngrok http 1000

# Terminal 2
python interactions.py
```

## Usage 💬

1. Add bot to your Slack workspace
2. First-time users select their preferred language from dropdown
3. Messages are automatically translated for users with different language preferences
4. Translations appear as private messages only you can see

## File Structure 📁

```
Slack_bot/
├── interactions.py           # Main bot application
├── requirements.txt         # Dependencies
├── user_preferences.json   # User language storage
└── .env                    # Environment variables
```

## Troubleshooting 🔍

- **Bot not responding**: Check ngrok URL is updated in Slack settings
- **Translation errors**: Verify Google API key and quota
- **Permission errors**: Ensure all required Slack scopes are added

## Deployment 🚀

For production, deploy to Heroku, Railway, or AWS and update Slack URLs accordingly.

---

**Happy translating! 🌍✨** 