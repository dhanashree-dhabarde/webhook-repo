# Deployment Guide for Webhook Receiver

## Issue Resolution

Your webhook endpoint is returning a 404/500 error. This is likely due to MongoDB connection issues or missing error handling in the production environment.

## Steps to Fix Your Hosted Application

### 1. Update Your Production Code

Replace your current `main.py` with the `main_production.py` file. This version includes:

- ✅ Better error handling for MongoDB connection failures
- ✅ Fallback to in-memory storage if MongoDB is unavailable
- ✅ Detailed logging for debugging
- ✅ Production-ready configuration
- ✅ Graceful degradation

### 2. Key Features of Production Version

- **Robust Error Handling**: Won't crash if MongoDB is unavailable
- **Fallback Storage**: Uses in-memory storage if MongoDB fails
- **Better Logging**: Detailed logs for debugging webhook issues
- **Production Ready**: Proper port configuration for hosting platforms

### 3. Verify Your Environment Variables

Make sure your hosting platform (Render) has these environment variables set:

```
MONGO_URI=mongodb+srv://dhanashreedhabarde:CdCu769MzMTPwX0y@cluster0.n9xx0xa.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
PORT=5000
```

### 4. Test Your Webhook Endpoint

After deployment, test your webhook endpoint:

**Test URL**: `https://webhook-repo-k7k1.onrender.com/webhook/receiver`

**Test Command**:
```bash
curl -X POST https://webhook-repo-k7k1.onrender.com/webhook/receiver \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: push" \
  -d '{
    "ref": "refs/heads/main",
    "pusher": {"name": "testuser"},
    "repository": {"full_name": "testuser/test-repo"}
  }'
```

### 5. GitHub Webhook Configuration

Once your endpoint is working, configure your GitHub webhook:

1. Go to your repository → Settings → Webhooks
2. Click "Add webhook"
3. **Payload URL**: `https://webhook-repo-k7k1.onrender.com/webhook/receiver`
4. **Content type**: `application/json`
5. **Events**: Select "Push events" and "Pull requests"
6. **Active**: ✅ Checked
7. Click "Add webhook"

### 6. Verify Webhook Delivery

After setting up:

1. **Check Webhook Status**: In GitHub webhook settings, you should see green checkmarks for successful deliveries
2. **Test with Real Events**: 
   - Push a commit to your repository
   - Create a pull request
   - Check your dashboard at `https://webhook-repo-k7k1.onrender.com/`

### 7. Debugging Steps

If you're still getting errors:

1. **Check Logs**: Review your hosting platform's logs
2. **Test Health Endpoint**: `https://webhook-repo-k7k1.onrender.com/health`
3. **Test API Endpoint**: `https://webhook-repo-k7k1.onrender.com/api/webhooks`

### 8. Common Issues & Solutions

**404 Error**: 
- Ensure the route `/webhook/receiver` exists in your deployed code
- Check that your main application file is properly configured

**500 Error**:
- Usually MongoDB connection issues
- The production version handles this gracefully with fallback storage

**No Data Showing**:
- Check that webhooks are being delivered by GitHub
- Verify the webhook URL is correct
- Check the GitHub webhook delivery logs

## Expected Behavior

After successful deployment:

1. ✅ Dashboard loads at `https://webhook-repo-k7k1.onrender.com/`
2. ✅ Webhook endpoint accepts POST requests
3. ✅ GitHub webhook deliveries show green checkmarks
4. ✅ Dashboard updates every 15 seconds with new activity
5. ✅ Messages display in exact PDF format:
   - "Travis pushed to main on 9th July 2025 - 7:30 PM UTC"
   - "Sarah submitted a pull request from feature to main on 9th July 2025 - 2:15 PM UTC"
   - "Mike merged branch hotfix to main on 9th July 2025 - 11:45 AM UTC"

## Final Verification

Test the complete flow:

1. **Deploy** the updated code
2. **Configure** GitHub webhook
3. **Push** a commit to your repository
4. **Check** your dashboard for the new activity
5. **Verify** the message format matches PDF requirements

Your webhook should now work correctly with the GitHub webhook configuration!
