from flask import Flask, request, jsonify
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import openai
import os

app = Flask(__name__)

# Replace with your actual tokens or load from environment variables
SLACK_BOT_TOKEN = 'xoxb-your-slack-bot-token'
OPENAI_API_KEY = 'your-openai-api-key'

client = WebClient(token=SLACK_BOT_TOKEN)
openai.api_key = OPENAI_API_KEY

@app.route("/standup", methods=["POST"])
def generate_standup():
    data = request.get_json()
    channel_id = data.get("channel_id")

    if not channel_id:
        return jsonify({"error": "channel_id is required"}), 400

    try:
        response = client.conversations_history(channel=channel_id, limit=50)
        messages = [msg['text'] for msg in response['messages']]

        combined_text = "\n".join(messages)

        ai_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Summarize these standup updates into Yesterday, Today, and Blockers."},
                {"role": "user", "content": combined_text}
            ]
        )

        summary = ai_response['choices'][0]['message']['content']
        return jsonify({"summary": summary})

    except SlackApiError as e:
        return jsonify({"error": f"Slack API error: {e.response['error']}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
@app.route('/')
def index():
    return '✅ Flask Standup API is running!'
