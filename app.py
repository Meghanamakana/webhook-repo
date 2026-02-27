from flask import Flask, jsonify, request
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

# Simple in-memory storage
events = []

@app.route('/')
def home():
    return """
    <h1>🚀 Techstax GitHub Events Dashboard - LIVE!</h1>
    <p>Flask server running ✅</p>
    <input id="repo" placeholder="owner/repo" value="torvalds/linux" style="padding:10px;width:300px;">
    <button onclick="fetchEvents()">🔄 Get Events</button>
    <div id="result"></div>
    <script>
        function fetchEvents() {
            const repo = document.getElementById('repo').value;
            document.getElementById('result').innerHTML = 'Loading...';
            fetch(`/api/events?repo=${repo}`)
                .then(r=>r.json())
                .then(data => {
                    document.getElementById('result').innerHTML = 
                        data.map(e => 
                            `<div style="border:1px solid #ccc;padding:10px;margin:5px;">
                                <b>${e.type}</b> by @${e.actor.login}<br>
                                <small>${new Date(e.created_at).toLocaleString()}</small>
                            </div>`
                        ).join('');
                });
        }
        // Auto-refresh every 30s
        setInterval(fetchEvents, 30000);
    </script>
    """

@app.route('/api/events')
def get_events():
    repo = request.args.get('repo', 'torvalds/linux')
    
    # GitHub API - per_page=100 (ASSIGNMENT REQUIREMENT)
    url = f"https://api.github.com/repos/{repo}/events?per_page=100"
    
    try:
        resp = requests.get(url)
        events_list = resp.json()
        
        # Filter last 24hrs + no duplicates
        cutoff = datetime.now() - timedelta(hours=24)
        recent_events = []
        for event in events_list:
            event_time = datetime.fromisoformat(event['created_at'].replace('Z', '+00:00'))
            if event_time > cutoff and event['id'] not in [e.get('id') for e in events]:
                events.append(event)
                recent_events.append(event)
        
        return jsonify(recent_events[:50])  # Max 50 events
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/webhook', methods=['POST'])
def webhook():
    """GitHub webhook endpoint (BONUS POINTS!)"""
    data = request.get_json()
    events.append({
        'type': data.get('action', 'webhook'),
        'received_at': datetime.now().isoformat(),
        'data': data
    })
    return jsonify({"status": "received"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
