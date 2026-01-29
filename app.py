from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# MongoDB connection - MUST be at module level (outside functions)
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
print(f"Connecting to MongoDB...")

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    # Test the connection
    client.server_info()
    print("✓ MongoDB connected successfully!")
    
    # Define database and collection at module level
    db = client['github_webhooks']
    events_collection = db['events']
    
    print(f"✓ Using database: github_webhooks")
    print(f"✓ Using collection: events")
    
except Exception as e:
    print(f"✗ MongoDB connection failed: {e}")
    # Create dummy collection for error handling
    client = None
    db = None
    events_collection = None


# ============= ROUTES =============

@app.route('/')
def index():
    """Render the main UI page"""
    return render_template('index.html')


@app.route('/webhook', methods=['POST'])
def webhook():
    """Receive GitHub webhook events"""
    print("\n" + "="*60)
    print("🔔 WEBHOOK RECEIVED!")
    print("="*60)
    
    # Check if MongoDB is connected
    if events_collection is None:
        print("❌ MongoDB not connected!")
        return jsonify({'status': 'error', 'message': 'Database not connected'}), 500
    
    try:
        # Get event type from headers
        event_type = request.headers.get('X-GitHub-Event')
        print(f"🎯 Event Type: {event_type}")
        
        # Get JSON data
        data = request.json
        if not data:
            print("❌ No JSON data received!")
            return jsonify({'status': 'error', 'message': 'No data'}), 400
        
        print(f"📦 Data keys: {list(data.keys())[:10]}")
        
        # Prepare event data
        event_data = {
            'request_id': str(data.get('hook_id', datetime.utcnow().timestamp())),
            'author': '',
            'action': '',
            'from_branch': '',
            'to_branch': '',
            'timestamp': datetime.utcnow()
        }
        
        # Handle PUSH event
        if event_type == 'push':
            print("✅ Processing PUSH event...")
            event_data['author'] = data['pusher']['name']
            event_data['action'] = 'push'
            event_data['to_branch'] = data['ref'].split('/')[-1]
            event_data['from_branch'] = ''
            print(f"  Author: {event_data['author']}")
            print(f"  Branch: {event_data['to_branch']}")
        
        # Handle PULL_REQUEST opened event
        elif event_type == 'pull_request' and data.get('action') == 'opened':
            print("✅ Processing PULL_REQUEST event...")
            event_data['author'] = data['pull_request']['user']['login']
            event_data['action'] = 'pull_request'
            event_data['from_branch'] = data['pull_request']['head']['ref']
            event_data['to_branch'] = data['pull_request']['base']['ref']
            print(f"  Author: {event_data['author']}")
            print(f"  From: {event_data['from_branch']} → To: {event_data['to_branch']}")
        
        # Handle MERGE event (when PR is merged)
        elif event_type == 'pull_request' and data.get('action') == 'closed' and data['pull_request'].get('merged'):
            print("✅ Processing MERGE event...")
            event_data['author'] = data['pull_request']['merged_by']['login']
            event_data['action'] = 'merge'
            event_data['from_branch'] = data['pull_request']['head']['ref']
            event_data['to_branch'] = data['pull_request']['base']['ref']
            print(f"  Author: {event_data['author']}")
            print(f"  From: {event_data['from_branch']} → To: {event_data['to_branch']}")
        
        else:
            print(f"⚠️ Unhandled event: {event_type}, action: {data.get('action')}")
            print("="*60 + "\n")
            return jsonify({'status': 'ignored'}), 200
        
        # Insert into MongoDB
        print("💾 Saving to MongoDB...")
        print(f"  Data: {event_data}")
        
        result = events_collection.insert_one(event_data)
        print(f"✅ Event stored with ID: {result.inserted_id}")
        
        print("="*60 + "\n")
        return jsonify({'status': 'success', 'id': str(result.inserted_id)}), 200
    
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        print("="*60 + "\n")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/events', methods=['GET'])
def get_events():
    """Get all events from MongoDB"""
    
    # Check if MongoDB is connected
    if events_collection is None:
        print("❌ MongoDB not connected in get_events!")
        return jsonify({'error': 'Database not connected'}), 500
    
    try:
        print("📊 Fetching events from MongoDB...")
        
        # Get latest 20 events, sorted by timestamp descending
        events = list(events_collection.find(
            {}, 
            {'_id': 0}  # Exclude MongoDB _id from response
        ).sort('timestamp', -1).limit(20))
        
        print(f"✓ Found {len(events)} events")
        
        # Format events for display
        formatted_events = []
        for event in events:
            message = ''
            
            if event['action'] == 'push':
                message = f"{event['author']} pushed to {event['to_branch']} on {format_timestamp(event['timestamp'])}"
            
            elif event['action'] == 'pull_request':
                message = f"{event['author']} submitted a pull request from {event['from_branch']} to {event['to_branch']} on {format_timestamp(event['timestamp'])}"
            
            elif event['action'] == 'merge':
                message = f"{event['author']} merged branch {event['from_branch']} to {event['to_branch']} on {format_timestamp(event['timestamp'])}"
            
            else:
                continue
            
            formatted_events.append({
                'message': message,
                'timestamp': event['timestamp'].isoformat()
            })
        
        print(f"✓ Returning {len(formatted_events)} formatted events")
        return jsonify(formatted_events), 200
    
    except Exception as e:
        print(f"❌ Error in get_events: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ============= HELPER FUNCTIONS =============

def format_timestamp(dt):
    """
    Format datetime to: "1st April 2021 - 9:30 PM UTC"
    """
    day = dt.day
    
    # Determine suffix (st, nd, rd, th)
    if 11 <= day <= 13:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
    
    # Format the datetime
    formatted = dt.strftime(f'%d{suffix} %B %Y - %I:%M %p UTC')
    
    # Replace leading zero in day (01 -> 1)
    formatted = formatted.replace(f'{day:02d}', f'{day}')
    
    return formatted


# ============= TEST ROUTE (for debugging) =============

@app.route('/test', methods=['GET'])
def test():
    """Test endpoint to verify MongoDB connection"""
    try:
        if events_collection is None:
            return jsonify({'status': 'error', 'message': 'MongoDB not connected'}), 500
        
        # Count documents
        count = events_collection.count_documents({})
        
        # Get one sample event
        sample = events_collection.find_one({})
        
        return jsonify({
            'status': 'success',
            'mongodb_connected': True,
            'total_events': count,
            'sample_event': str(sample) if sample else None
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ============= MAIN =============

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Starting Flask Application")
    print("="*60)
    print(f"📍 Server: http://localhost:5000")
    print(f"📍 Test endpoint: http://localhost:5000/test")
    print(f"📍 Events API: http://localhost:5000/api/events")
    print(f"📍 Webhook: http://localhost:5000/webhook")
    print("="*60 + "\n")
    
    app.run(debug=True, port=5000, host='0.0.0.0')