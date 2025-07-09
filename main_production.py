from flask import Flask, request, jsonify, render_template
from flask_pymongo import PyMongo
from datetime import datetime
import json
import os
from werkzeug.exceptions import BadRequest
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB Configuration
app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb+srv://dhanashreedhabarde:CdCu769MzMTPwX0y@cluster0.n9xx0xa.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

# Initialize MongoDB with error handling
mongo = None
try:
    mongo = PyMongo(app)
    logger.info("MongoDB initialized successfully")
except Exception as e:
    logger.error(f"MongoDB initialization failed: {e}")
    mongo = None

# In-memory fallback storage
webhook_data = []

def get_webhook_collection():
    """Get MongoDB collection or return None if not available"""
    try:
        if mongo and mongo.db:
            return mongo.db.webhooks
        else:
            logger.warning("MongoDB not available, using in-memory storage")
            return None
    except Exception as e:
        logger.error(f"MongoDB connection error: {e}")
        return None

def parse_github_webhook(payload, headers):
    """Parse GitHub webhook payload and extract relevant information"""
    try:
        event_type = headers.get('X-GitHub-Event', 'unknown')
        
        if event_type == 'push':
            return {
                'action': 'PUSH',
                'author': payload.get('pusher', {}).get('name', 'Unknown'),
                'to_branch': payload.get('ref', '').replace('refs/heads/', ''),
                'from_branch': None,
                'timestamp': datetime.utcnow(),
                'repository': payload.get('repository', {}).get('full_name', 'Unknown'),
                'event_type': event_type,
                'raw_payload': payload
            }
        
        elif event_type == 'pull_request':
            pr_data = payload.get('pull_request', {})
            return {
                'action': 'PULL_REQUEST',
                'author': pr_data.get('user', {}).get('login', 'Unknown'),
                'from_branch': pr_data.get('head', {}).get('ref', 'Unknown'),
                'to_branch': pr_data.get('base', {}).get('ref', 'Unknown'),
                'timestamp': datetime.utcnow(),
                'repository': payload.get('repository', {}).get('full_name', 'Unknown'),
                'event_type': event_type,
                'raw_payload': payload
            }
        
        elif event_type == 'pull_request' and payload.get('action') == 'closed' and payload.get('pull_request', {}).get('merged'):
            # This handles merge events
            pr_data = payload.get('pull_request', {})
            return {
                'action': 'MERGE',
                'author': pr_data.get('merged_by', {}).get('login', 'Unknown'),
                'from_branch': pr_data.get('head', {}).get('ref', 'Unknown'),
                'to_branch': pr_data.get('base', {}).get('ref', 'Unknown'),
                'timestamp': datetime.utcnow(),
                'repository': payload.get('repository', {}).get('full_name', 'Unknown'),
                'event_type': event_type,
                'raw_payload': payload
            }
        
        else:
            # Generic handler for other events
            return {
                'action': event_type.upper(),
                'author': 'Unknown',
                'from_branch': None,
                'to_branch': None,
                'timestamp': datetime.utcnow(),
                'repository': payload.get('repository', {}).get('full_name', 'Unknown'),
                'event_type': event_type,
                'raw_payload': payload
            }
    
    except Exception as e:
        logger.error(f"Error parsing webhook: {e}")
        return None

@app.route('/')
def dashboard():
    """Render the dashboard"""
    return render_template('dashboard.html')

@app.route('/webhook/receiver', methods=['POST'])
def webhook_receiver():
    """Main webhook receiver endpoint"""
    try:
        # Get headers
        headers = dict(request.headers)
        logger.info(f"Received webhook with headers: {headers}")
        
        # Get payload
        if request.is_json:
            payload = request.get_json()
        else:
            payload = request.form.to_dict()
        
        logger.info(f"Webhook payload: {payload}")
        
        # Parse the webhook
        parsed_data = parse_github_webhook(payload, headers)
        
        if parsed_data:
            # Try to store in MongoDB first, fallback to memory
            collection = get_webhook_collection()
            if collection is not None:
                try:
                    result = collection.insert_one(parsed_data)
                    logger.info(f"Stored webhook in MongoDB: {result.inserted_id}")
                except Exception as e:
                    logger.error(f"MongoDB storage failed: {e}")
                    # Fallback to in-memory storage
                    webhook_data.append(parsed_data)
                    logger.info("Stored webhook in memory as fallback")
            else:
                # Store in memory
                webhook_data.append(parsed_data)
                logger.info("Stored webhook in memory")
            
            return jsonify({
                'status': 'success',
                'message': 'Webhook received and processed',
                'id': str(len(webhook_data)),
                'action': parsed_data['action']
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to parse webhook payload'
            }), 400
    
    except BadRequest:
        return jsonify({
            'status': 'error',
            'message': 'Invalid JSON payload'
        }), 400
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Internal server error: {str(e)}'
        }), 500

@app.route('/api/webhooks', methods=['GET'])
def get_webhooks():
    """API endpoint to get webhook data for UI polling"""
    try:
        # Get query parameters
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        # Try MongoDB first, fallback to memory
        collection = get_webhook_collection()
        if collection is not None:
            try:
                webhooks = list(collection.find()
                               .sort('timestamp', -1)
                               .skip(offset)
                               .limit(limit))
            except Exception as e:
                logger.error(f"MongoDB query failed: {e}")
                # Fallback to in-memory data
                sorted_webhooks = sorted(webhook_data, key=lambda x: x['timestamp'], reverse=True)
                webhooks = sorted_webhooks[offset:offset+limit]
        else:
            # Use in-memory data
            sorted_webhooks = sorted(webhook_data, key=lambda x: x['timestamp'], reverse=True)
            webhooks = sorted_webhooks[offset:offset+limit]
        
        # Format webhooks for UI
        formatted_webhooks = []
        for webhook in webhooks:
            # Format timestamp exactly as specified in PDF
            day = webhook['timestamp'].day
            if day == 1 or day == 21 or day == 31:
                day_suffix = 'st'
            elif day == 2 or day == 22:
                day_suffix = 'nd'
            elif day == 3 or day == 23:
                day_suffix = 'rd'
            else:
                day_suffix = 'th'
            
            timestamp = webhook['timestamp'].strftime(f'{day}{day_suffix} %B %Y - %I:%M %p UTC')
            
            # Create display message based on action - exactly as specified in PDF
            if webhook['action'] == 'PUSH':
                message = f"{webhook['author']} pushed to {webhook['to_branch']} on {timestamp}"
            elif webhook['action'] == 'PULL_REQUEST':
                message = f"{webhook['author']} submitted a pull request from {webhook['from_branch']} to {webhook['to_branch']} on {timestamp}"
            elif webhook['action'] == 'MERGE':
                message = f"{webhook['author']} merged branch {webhook['from_branch']} to {webhook['to_branch']} on {timestamp}"
            else:
                message = f"{webhook['author']} performed {webhook['action']} on {timestamp}"
            
            formatted_webhooks.append({
                'id': str(webhook.get('_id', len(webhook_data))),
                'action': webhook['action'],
                'message': message,
                'author': webhook['author'],
                'from_branch': webhook['from_branch'],
                'to_branch': webhook['to_branch'],
                'timestamp': timestamp,
                'repository': webhook['repository'],
                'event_type': webhook['event_type']
            })
        
        return jsonify({
            'status': 'success',
            'data': formatted_webhooks,
            'count': len(formatted_webhooks)
        })
    
    except Exception as e:
        logger.error(f"Error fetching webhooks: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to fetch webhooks: {str(e)}'
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """API endpoint to get webhook statistics"""
    try:
        # Try MongoDB first, fallback to memory
        collection = get_webhook_collection()
        if collection is not None:
            try:
                total_webhooks = collection.count_documents({})
                
                # Get today's webhooks
                today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                today_webhooks = collection.count_documents({
                    'timestamp': {'$gte': today_start}
                })
                
                # Get action counts
                pipeline = [
                    {'$group': {'_id': '$action', 'count': {'$sum': 1}}}
                ]
                action_counts = list(collection.aggregate(pipeline))
            except Exception as e:
                logger.error(f"MongoDB stats query failed: {e}")
                # Fallback to in-memory data
                total_webhooks = len(webhook_data)
                today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                today_webhooks = len([w for w in webhook_data if w['timestamp'] >= today_start])
                
                action_counts = {}
                for webhook in webhook_data:
                    action = webhook['action']
                    action_counts[action] = action_counts.get(action, 0) + 1
                
                action_counts = [{'_id': action, 'count': count} for action, count in action_counts.items()]
        else:
            # Use in-memory data
            total_webhooks = len(webhook_data)
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            today_webhooks = len([w for w in webhook_data if w['timestamp'] >= today_start])
            
            action_counts = {}
            for webhook in webhook_data:
                action = webhook['action']
                action_counts[action] = action_counts.get(action, 0) + 1
            
            action_counts = [{'_id': action, 'count': count} for action, count in action_counts.items()]
        
        return jsonify({
            'status': 'success',
            'data': {
                'total_webhooks': total_webhooks,
                'today_webhooks': today_webhooks,
                'action_counts': action_counts
            }
        })
    
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to fetch statistics: {str(e)}'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'webhook-receiver',
        'mongodb_status': 'connected' if mongo else 'disconnected'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
