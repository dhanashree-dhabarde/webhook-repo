import requests
import json

# Test webhook endpoint
def test_webhook():
    url = "http://localhost:5000/webhook/receiver"
    
    # Sample GitHub push payload
    push_payload = {
        "ref": "refs/heads/main",
        "pusher": {
            "name": "testuser"
        },
        "repository": {
            "full_name": "testuser/test-repo"
        }
    }
    
    headers = {
        "X-GitHub-Event": "push",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=push_payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook test successful!")
        else:
            print("❌ Webhook test failed!")
            
    except Exception as e:
        print(f"Error testing webhook: {e}")

if __name__ == "__main__":
    test_webhook()
