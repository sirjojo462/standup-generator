# main.py
import openai
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import logging  # Import logging module
from dotenv import load_dotenv
import os
from prometheus_flask_exporter import PrometheusMetrics
from pythonjsonlogger import jsonlogger

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set log level to INFO
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log format
    handlers=[
        logging.StreamHandler(),  # Log to console
        logging.FileHandler("app.log", mode='a')  # Log to a file
    ]
)

log_handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(message)s')
log_handler.setFormatter(formatter)
logging.getLogger().addHandler(log_handler)

load_dotenv()  # Load environment variables from .env
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
CORS(app)

metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Application info', version='1.0.0')

# Store standup history (in production, use a database)
standup_history = {}

@app.route('/')
def home():
    logging.info("Home endpoint accessed")  # Log access to the home endpoint
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

@app.route('/standup', methods=['POST'])
def generate_standup():
    """Endpoint that generates standup summaries"""
    data = request.json
    logging.info("Received request to generate standup: %s", data)  # Log incoming request data
    
    # Validate input
    if not data or 'channel_id' not in data:
        logging.warning("Invalid request: Missing channel_id parameter")  # Log warning for invalid input
        return jsonify({"error": "Missing channel_id parameter"}), 400
    
    channel_id = data['channel_id']
    
    # Generate timestamp for the standup
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create standup summary (in a real app, this would call Slack API + AI)
    summary = f"""🚀 Standup Summary for Channel {channel_id} - {timestamp}

✅ Completed Yesterday:
- Fixed authentication bug (JIRA
