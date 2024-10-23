import requests

# Add the Bearer Token you obtained from get_bearer_token.py here
bearer_token = 'YOUR_BEARER_TOKEN'  # Replace with your actual Bearer Token

def make_request():
    url = "https://api.twitter.com/2/tweets"
    headers = {
        "Authorization": f"Bearer {bearer_token}"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        print(response.json())
    else:
        print(f"Request failed: {response.status_code} - {response.text}")

if __name__ == "__main__":
    make_request()
