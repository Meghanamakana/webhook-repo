from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# In-memory storage (works perfectly for demo)
events_db = []

@app.route('/')
def dashboard():
    # Filter last 24hr events
    cutoff = datetime.now() - timedelta(hours=24)
    recent_events = [e for e in events_db if e.get('created_at', datetime.now()) > cutoff]
    return render_template('index.html', events=recent_events)

@app.route('/api/events')
def fetch_events():
    repo = request.args.get('repo', 'octocat/Hello-World')
    
    # GitHub API - per_page=100 (ASSIGNMENT REQUIREMENT)
    url = f"https://api.github.com/repos/{repo}/events?per_page=100"
    response = requests.get(url)
    events = response.json()
    
    # Add to "database" (no duplicates by ID)
    for event in events:
        if not any(e.get('id') == event['id'] for e in events_db):
            event['created_at'] = datetime.fromisoformat(
                event['created_at'].replace('Z', '+00:00')
            )
            events_db.append(event)
    
    return jsonify(events)

@app.route('/webhook', methods=['POST'])
def github_webhook():
    data = request.get_json()
    data['received_at'] = datetime.now()
    events_db.append(data)
    print(f"✅ Webhook received: {data.get('action', 'event')}")
    return jsonify({"status": "received"}), 200

@app.route('/clear')
def clear_db():
    global events_db
    events_db = []
    return "Database cleared!"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
