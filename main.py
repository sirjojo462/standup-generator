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

app = Flask(__name__)
CORS(app)

# JWT Configuration
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Replace with a strong secret key
jwt = JWTManager(app)

# Store standup history (in production, use a database)
standup_history = {}

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

    # Replace this with your actual user authentication logic
    if username == "admin" and password == "01234":  # Example credentials
        access_token = create_access_token(identity=username)
        return jsonify({"access_token": access_token}), 200

if __name__ == '__main__':
    logging.info("Starting the Flask application")
    print("Flask application is starting...")
    app.run(host='0.0.0.0', port=5000, debug=True)

