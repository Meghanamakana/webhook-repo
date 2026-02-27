// Techstax Assignment Solution - COMPLETE WORKING CODE
let events = [];
let lastRefreshTime = null;
const REFRESH_INTERVAL = 30000; // 30 seconds auto-refresh

// DOM elements
const repoInput = document.getElementById('repoInput');
const eventsContainer = document.getElementById('eventsContainer');
const lastRefreshEl = document.getElementById('lastRefresh');
const eventCountEl = document.getElementById('eventCount');

// 1. MAIN FUNCTION: Fetch GitHub events (per_page=100)
async function fetchEvents() {
    try {
        const repo = repoInput.value.trim();
        if (!repo.includes('/')) {
            alert('Format: owner/repo (like: octocat/Hello-World)');
            return;
        }

        eventsContainer.innerHTML = '<div class="no-events">🔄 Loading...</div>';

        // GitHub API - exactly as required (per_page=100)
        const response = await fetch(`https://api.github.com/repos/${repo}/events?per_page=100`);
        if (!response.ok) throw new Error(`Error: ${response.status}`);

        const newEvents = await response.json();
        
        // Filter: Last 24hrs ONLY + NO DUPLICATES
        const now = Date.now();
        const filteredEvents = newEvents
            .filter(event => (now - new Date(event.created_at).getTime()) < 86400000) // 24hrs
            .filter(event => !events.some(e => e.id === event.id)) // No duplicates
            .slice(0, 50); // Max 50 new events

        // Add new events to top
        events = filteredEvents.concat(events).slice(0, 100);
        lastRefreshTime = new Date().toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' });
        
        updateUI();
        console.log(`✅ ${filteredEvents.length} new events. Total: ${events.length}`);
        
    } catch (error) {
        eventsContainer.innerHTML = `<div class="no-events">❌ ${error.message}</div>`;
    }
}

// 2. Update display
function updateUI() {
    lastRefreshEl.textContent = `Last refresh: ${lastRefreshTime}`;
    eventCountEl.textContent = `${events.length} events`;
    
    if (events.length === 0) {
        eventsContainer.innerHTML = '<div class="no-events">No recent events (last 24hrs)</div>';
        return;
    }

    eventsContainer.innerHTML = events.map(createEventHTML).join('');
}

// 3. Create event card
function createEventHTML(event) {
    const actor = event.actor;
    const timeAgo = formatTimeAgo(event.created_at);
    
    return `
        <div class="event">
            <div class="event-header">
                <img class="actor-avatar" src="${actor.avatar_url}" alt="${actor.login}" loading="lazy">
                <div class="event-meta">
                    <div class="event-type">${event.type} by <strong>@${actor.login}</strong></div>
                    <div class="event-time">${timeAgo}</div>
                </div>
            </div>
            <div class="event-details">${formatEventDetails(event)}</div>
        </div>
    `;
}

// 4. Event details formatter
function formatEventDetails(event) {
    const payload = event.payload;
    switch(event.type) {
        case 'PushEvent':
            return `<strong>${payload.size} commits</strong> to <code>${payload.ref.replace('refs/heads/', '')}</code>`;
        case 'PullRequestEvent':
            return `PR #${payload.number}: ${payload.action} - ${payload.pull_request.title}`;
        case 'IssuesEvent':
            return `Issue #${payload.issue.number}: ${payload.action}`;
        default:
            return `Event: ${event.type}`;
    }
}

// 5. Time ago formatter (handles dates correctly)
function formatTimeAgo(dateStr) {
    const now = new Date();
    const eventTime = new Date(dateStr);
    const diffMs = now - eventTime;
    
    if (diffMs < 60000) return 'Just now';
    if (diffMs < 3600000) return `${Math.floor(diffMs/60000)} min ago`;
    if (diffMs < 86400000) return `${Math.floor(diffMs/3600000)} hr ago`;
    return `${Math.floor(diffMs/86400000)} day ago`;
}

// 6. Clear button
function clearEvents() {
    events = [];
    updateUI();
}

// 7. START: Auto-refresh + initial load
setInterval(fetchEvents, REFRESH_INTERVAL);
document.addEventListener('DOMContentLoaded', fetchEvents);
