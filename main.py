# main.py
import openai
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
CORS(app)

# Store standup history (in production, use a database)
standup_history = {}

@app.route('/')
def home():
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
    
    # Validate input
    if not data or 'channel_id' not in data:
        return jsonify({"error": "Missing channel_id parameter"}), 400
    
    channel_id = data['channel_id']
    
    # Generate timestamp for the standup
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create standup summary (in a real app, this would call Slack API + AI)
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
    
    # Store in history
    standup_history[channel_id] = {
        "timestamp": timestamp,
        "summary": summary
    }
    
    return jsonify({
        "status": "success",
        "channel_id": channel_id,
        "summary": summary,
        "generated_at": timestamp
    })

@app.route('/standup/history', methods=['GET'])
def get_history():
    """Returns all generated standups"""
    return jsonify({
        "count": len(standup_history),
        "standups": standup_history
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
 
