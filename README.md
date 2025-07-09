# GitHub Webhook Dashboard

A Flask-based application that receives GitHub webhooks and displays repository activity in real-time.

## Features

- **Real-time GitHub Webhook Processing**: Captures Push, Pull Request, and Merge events
- **MongoDB Storage**: Stores webhook data with proper schema
- **Live Dashboard**: Displays activity with 15-second polling updates
- **Clean UI**: Minimal, professional interface showing formatted messages
- **Message Formats**: Exactly as specified in requirements:
  - PUSH: `{author} pushed to {to_branch} on {timestamp}`
  - PULL_REQUEST: `{author} submitted a pull request from {from_branch} to {to_branch} on {timestamp}`
  - MERGE: `{author} merged branch {from_branch} to {to_branch} on {timestamp}`

## Project Structure

```
TECHSTAX/
├── main.py                 # Main Flask application
├── templates/
│   └── dashboard.html      # Clean dashboard UI
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables
└── README.md              # This file
```

## Prerequisites

- Python 3.7+
- MongoDB Atlas account (or local MongoDB)
- Git repository for webhook testing

## Installation

1. **Clone/Download the project**
   ```bash
   cd C:\Users\91976\Downloads\TECHSTAX
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**
   
   Update `.env` file with your MongoDB connection string:
   ```
   MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/database
   FLASK_ENV=development
   FLASK_DEBUG=True
   PORT=5000
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

   The application will start on `http://localhost:5000`

## MongoDB Schema

The application stores webhook data in the following format:

```json
{
  "action": "PUSH|PULL_REQUEST|MERGE",
  "author": "github_username",
  "from_branch": "source_branch",
  "to_branch": "target_branch", 
  "timestamp": "ISODate",
  "repository": "owner/repo_name",
  "event_type": "push|pull_request",
  "raw_payload": {...}
}
```

## Webhook Setup

1. **Create a GitHub Repository** (action-repo)
2. **Configure Webhook**:
   - Go to repository Settings → Webhooks
   - Add webhook URL: `https://your-domain.com/webhook/receiver`
   - Select events: Push, Pull requests
   - Content type: `application/json`

## API Endpoints

- `GET /` - Dashboard interface
- `POST /webhook/receiver` - GitHub webhook endpoint
- `GET /api/webhooks` - Fetch webhook data (supports limit, offset)
- `GET /api/stats` - Get webhook statistics
- `GET /health` - Health check

## Dashboard Features

- **Live Updates**: Polls for new data every 15 seconds
- **Activity Feed**: Shows recent repository activity
- **Status Indicator**: Visual confirmation of live updates
- **Clean Design**: Minimal interface focused on webhook messages
- **Responsive Layout**: Works on desktop and mobile

## Testing

To test the webhook receiver:

1. **Start the application**
2. **Create test events** in your GitHub repository:
   - Push commits to different branches
   - Create pull requests
   - Merge branches
3. **Monitor the dashboard** for real-time updates

## Production Deployment

For production deployment:

1. **Update environment variables** for production
2. **Use a production WSGI server** (e.g., Gunicorn)
3. **Set up reverse proxy** (e.g., Nginx)
4. **Configure SSL** for webhook security
5. **Set up monitoring** and logging

## Message Format Examples

- **PUSH**: "John pushed to main on 9th July 2025 - 7:30 PM UTC"
- **PULL_REQUEST**: "Sarah submitted a pull request from feature-branch to main on 9th July 2025 - 2:15 PM UTC"  
- **MERGE**: "Mike merged branch hotfix to main on 9th July 2025 - 11:45 AM UTC"

## Requirements Compliance

This project fulfills all requirements from the assessment:

✅ GitHub webhook integration (Push, Pull Request, Merge)  
✅ MongoDB storage with proper schema  
✅ UI polling every 15 seconds  
✅ Exact message formats as specified  
✅ Clean, minimal design  
✅ Flask implementation  
✅ Real-time activity display  

## Support

For issues or questions, please check the console logs and ensure:
- MongoDB connection is working
- GitHub webhook is properly configured
- All dependencies are installed
- Port 5000 is available
