from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from datetime import datetime, timedelta
import requests
import os

app = Flask(__name__)

# FREE MongoDB Atlas (replace with your connection string later)
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/github_events')
client = MongoClient(MONGO_URI)
db = client.github_events
events_collection = db.events

@app.route('/')
def dashboard():
    # Get last 24hr events from MongoDB
    cutoff = datetime.now() - timedelta(hours=24)
    recent_events = list(events_collection.find({
        "created_at": {"$gte": cutoff}
    }).sort("created_at", -1).limit(100))
    
    return render_template('index.html', events=recent_events)

@app.route('/api/events')
def fetch_events():
    repo = request.args.get('repo', 'octocat/Hello-World')
    
    # GitHub API call - per_page=100 (ASSIGNMENT REQUIREMENT)
    url = f"https://api.github.com/repos/{repo}/events?per_page=100"
    response = requests.get(url)
    events = response.json()
    
    # Save NEW events only (no duplicates)
    for event in events:
        if not events_collection.find_one({"id": event["id"]}):
            event["created_at"] = datetime.fromisoformat(
                event["created_at"].replace('Z', '+00:00')
            )
            events_collection.insert_one(event)
    
    return jsonify(events)

@app.route('/webhook', methods=['POST'])
def github_webhook():
    """GitHub webhook receiver (BONUS POINTS!)"""
    data = request.get_json()
    data["received_at"] = datetime.now()
    events_collection.insert_one(data)
    print(f"Webhook: {data.get('action', 'event')}")
    return jsonify({"status": "received"}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
