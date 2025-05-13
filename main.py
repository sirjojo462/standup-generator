# main.py
import openai
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime
import logging
from dotenv import load_dotenv
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import sqlite3

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log", mode='a')
    ]
)

load_dotenv()  # Load environment variables from .env
openai.api_key = os.getenv("OPENAI_API_KEY")
slack_client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))

print("OPENAI_API_KEY:", os.getenv("OPENAI_API_KEY"))
print("SLACK_BOT_TOKEN:", os.getenv("SLACK_BOT_TOKEN"))
print("JWT_SECRET_KEY:", os.getenv("JWT_SECRET_KEY"))

app = Flask(__name__)
CORS(app)

# JWT Configuration
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Replace with a strong secret key
jwt = JWTManager(app)

# Initialize SQLite database
conn = sqlite3.connect("standup.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS standups (
        channel_id TEXT,
        timestamp TEXT,
        summary TEXT
    )
""")
conn.commit()

@app.route('/')
def home():
    logging.info("Home endpoint accessed")
    return """
    <html>
    <head>
        <title>JJ AI Standup Generator</title>
    </head>
    <body>
        <h1>Backend Service is Running</h1>
        <p>The standup generator API is ready to receive requests.</p>
    </body>
    </html>
    """

@app.route('/login', methods=['POST'])
def login():
    """Login endpoint to authenticate users and issue JWT tokens"""
    data = request.json
    username = data.get('username')
    password = data.get('password')

    # Validate input
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    # Replace this with your actual user authentication logic
    if username == "admin" and password == "01234":  # Example credentials
        access_token = create_access_token(identity=username)
        return jsonify({"access_token": access_token}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@app.route('/standup', methods=['POST'])
@jwt_required()
def generate_standup():
    """Endpoint that generates standup summaries"""
    current_user = get_jwt_identity()  # Get the identity of the logged-in user
    logging.info(f"Standup requested by user: {current_user}")

    data = request.json
    if not data or 'channel_id' not in data:
        return jsonify({"error": "Missing channel_id parameter"}), 400

    channel_id = data['channel_id']
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Generate a standup summary (replace with AI logic if needed)
    summary = f"""🚀 Standup Summary for Channel {channel_id} - {timestamp}

✅ Completed Yesterday:
- Fixed authentication bug (JIRA-123)
- Implemented new dashboard UI
- Conducted code reviews

📅 Planning Today:
- Refactor notification service
- Write integration tests
- Team sync meeting at 2pm

🛑 Blockers:
- Need API docs from backend team
- Waiting on design assets

💡 Suggestions:
- Consider using Redis for caching
- Schedule tech debt discussion"""

    # Store in SQLite database
    try:
        cursor.execute("INSERT INTO standups (channel_id, timestamp, summary) VALUES (?, ?, ?)",
                       (channel_id, timestamp, summary))
        conn.commit()
    except Exception as e:
        logging.error(f"Database error: {e}")
        return jsonify({"error": "Failed to store standup summary"}), 500

    # Optionally send to Slack
    try:
        response = slack_client.chat_postMessage(
            channel=channel_id,
            text=summary
        )
        logging.info(f"Message sent to Slack: {response['ts']}")
    except SlackApiError as e:
        logging.error(f"Error sending message to Slack: {e.response['error']}")

    return jsonify({
        "status": "success",
        "channel_id": channel_id,
        "summary": summary,
        "generated_at": timestamp
    })

@app.route('/standup/history', methods=['GET'])
@jwt_required()
def get_history():
    """Returns all generated standups"""
    current_user = get_jwt_identity()  # Get the identity of the logged-in user
    logging.info(f"History accessed by user: {current_user}")

    try:
        cursor.execute("SELECT channel_id, timestamp, summary FROM standups")
        rows = cursor.fetchall()
        history = [{"channel_id": row[0], "timestamp": row[1], "summary": row[2]} for row in rows]
    except Exception as e:
        logging.error(f"Database error: {e}")
        return jsonify({"error": "Failed to retrieve standup history"}), 500

    return jsonify({
        "count": len(history),
        "standups": history
    })

@app.errorhandler(Exception)
def handle_exception(e):
    logging.error(f"Unhandled Exception: {e}")
    return jsonify({"error": "An unexpected error occurred"}), 500

if __name__ == '__main__':
    logging.info("Starting the Flask application")
    print("Flask application is starting...")
    app.run(host='0.0.0.0', port=5000)
