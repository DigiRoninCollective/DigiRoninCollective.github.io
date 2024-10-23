import base64
import requests

# Your Twitter App's credentials
client_id = 'RHY3UFNZRjhiWjdobjc5UC0yalo6MTpjaQ'  # Replace with your Client ID
client_secret = '1Lg66-SLlt3ykDvL8aueJEs0poK6GRGndorYIu_EIdaxoppHbZ'  # Replace with your Client Secret
token_url = "https://api.twitter.com/oauth2/token"

def get_bearer_token():
    # Encode client ID and secret
    auth_credentials = f"{client_id}:{client_secret}".encode('ascii')
    b64_encoded_credentials = base64.b64encode(auth_credentials).decode('ascii')
    
    # Prepare headers
    headers = {
        "Authorization": f"Basic {b64_encoded_credentials}",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"
    }
    
    # Prepare data for the request
    data = {'grant_type': 'client_credentials'}
    
    # Make the POST request
    response = requests.post(token_url, headers=headers, data=data)
    
    print(f"Response Status Code: {response.status_code}")
    print(f"Response Text: {response.text}")
    
    if response.status_code == 200:
        # Extract the bearer token from the response
        bearer_token = response.json()['access_token']
        print(f"Bearer token: {bearer_token}")
        return bearer_token
    else:
        print(f"Failed to get bearer token: {response.status_code} - {response.text}")
        return None

if __name__ == "__main__":
    token = get_bearer_token()
