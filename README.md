# GitHub Webhook Receiver

A Flask-based webhook receiver that captures GitHub events (Push, Pull Request, Merge) and displays them in a clean web interface with real-time polling.

## 🚀 Features

- ✅ Receives GitHub webhooks for Push, Pull Request, and Merge events
- ✅ Stores events in MongoDB with complete metadata
- ✅ Real-time UI updates every 15 seconds
- ✅ Clean and minimal interface
- ✅ RESTful API for event retrieval
- ✅ Detailed logging for debugging

## 📋 Prerequisites

- Python 3.8 or higher
- MongoDB (Atlas or local installation)
- GitHub account
- ngrok (for local development) or a hosting platform

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/KaushalAvinash/webhook-repo.git
cd webhook-repo
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# On macOS/Linux
source venv/bin/activate

# On Windows
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up MongoDB

**Option A: MongoDB Atlas (Cloud - Recommended)**

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a free cluster
3. Create a database user
4. Whitelist your IP (or allow from anywhere: `0.0.0.0/0`)
5. Get your connection string

**Option B: Local MongoDB**
```bash
# On macOS
brew install mongodb-community
brew services start mongodb-community

# On Ubuntu/Debian
sudo apt-get install mongodb
sudo systemctl start mongodb
```

### 5. Configure Environment Variables

Create a `.env` file in the root directory:
```env
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/github_webhooks?retryWrites=true&w=majority
```

Replace with your actual MongoDB connection string.

## 🚦 Running the Application

### Local Development
```bash
python app.py
```

The application will start on `http://localhost:5000`

### Expose Local Server (for GitHub webhooks)

Use ngrok to create a public URL:
```bash
ngrok http 5000
```

Copy the HTTPS URL (e.g., `https://abcd-1234.ngrok-free.app`)

## 📡 API Endpoints

### `GET /`
Main UI page displaying GitHub events

### `POST /webhook`
Webhook endpoint for receiving GitHub events

**Headers:**
- `X-GitHub-Event`: Event type (push, pull_request)
- `Content-Type`: application/json

### `GET /api/events`
Returns list of formatted events

**Response:**
```json
[
  {
    "message": "john pushed to main on 29th January 2025 - 10:30 AM UTC",
    "timestamp": "2025-01-29T10:30:00"
  }
]
```

### `GET /test`
Test endpoint to verify MongoDB connection

## 🗄️ MongoDB Schema
```javascript
{
  "request_id": String,      // Unique webhook ID
  "author": String,          // GitHub username
  "action": String,          // "push", "pull_request", or "merge"
  "from_branch": String,     // Source branch (for PR/merge)
  "to_branch": String,       // Target/pushed branch
  "timestamp": DateTime      // UTC timestamp
}
```

## 🎨 Project Structure
```
webhook-repo/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not in git)
├── .gitignore            # Git ignore file
├── README.md             # This file
├── templates/
│   └── index.html        # Main UI template
├── static/
│   └── style.css         # Stylesheet
└── venv/                 # Virtual environment (not in git)
```

## 🧪 Testing

### Test MongoDB Connection
```bash
python -c "from pymongo import MongoClient; import os; from dotenv import load_dotenv; load_dotenv(); client = MongoClient(os.getenv('MONGO_URI')); print('✓ Connected!' if client.server_info() else '✗ Failed')"
```

### Test Webhook Endpoint
```bash
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: push" \
  -d '{"pusher":{"name":"TestUser"},"ref":"refs/heads/main"}'
```

### Access Test Endpoint

Visit: `http://localhost:5000/test`

## 🌐 Deployment

### Deploy to Render

1. Push code to GitHub
2. Go to [Render](https://render.com)
3. Create new Web Service
4. Connect your repository
5. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Environment Variables**: Add `MONGO_URI`
6. Deploy!

### Deploy to Railway

1. Push code to GitHub
2. Go to [Railway](https://railway.app)
3. Create new project from GitHub repo
4. Add environment variable: `MONGO_URI`
5. Deploy automatically

### Deploy to Heroku
```bash
# Install Heroku CLI
heroku login
heroku create your-app-name

# Set environment variable
heroku config:set MONGO_URI="your_mongodb_uri"

# Deploy
git push heroku main
```

## 🔧 Troubleshooting

### MongoDB Connection Failed

- Verify connection string in `.env`
- Check MongoDB Atlas IP whitelist
- Ensure database user has correct permissions
- Test with: `http://localhost:5000/test`

### Webhook Not Receiving Events

- Check ngrok is running and URL matches GitHub webhook
- Verify webhook endpoint is `https://your-url/webhook` (with `/webhook`)
- Check GitHub webhook "Recent Deliveries" for errors
- Look at Flask console for error messages

### UI Shows "Error loading events"

- Check browser console (F12) for errors
- Verify `/api/events` endpoint returns data
- Ensure MongoDB connection is active
- Check Flask terminal for error logs

## 📝 Event Format Examples

**Push Event:**
```
john pushed to main on 29th January 2025 - 10:30 AM UTC
```

**Pull Request Event:**
```
jane submitted a pull request from feature/login to main on 29th January 2025 - 09:15 AM UTC
```

**Merge Event:**
```
john merged branch feature/login to main on 29th January 2025 - 11:45 AM UTC
```

## 🔗 Related Repository

- [action-repo](https://github.com/KaushalAvinash/action-repo) - GitHub repository that triggers webhooks

## 👤 Author

**AVINASH KAUSHAL**
- GitHub: [KaushalAvinash](https://github.com/KaushalAvinash)

## 🙏 Acknowledgments

- Built as part of Developer Assessment Task
- Uses Flask for web framework
- MongoDB for data persistence
- GitHub Webhooks for event notifications