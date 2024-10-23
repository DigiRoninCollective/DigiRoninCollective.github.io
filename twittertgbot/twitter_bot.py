import telebot
import tweepy
import logging
import requests
import json
import threading
import time

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Twitter API credentials
DEFAULT_TWITTER_API_KEY = 'lM2Z7MSXpQKeZmZAdPUVMLqhK'
DEFAULT_TWITTER_API_SECRET = '7Aam8ubN4Hkp90OSCu5jF0zscWgDprLN5JGtv04msSCFMgiSrJ'
DEFAULT_TWITTER_ACCESS_TOKEN = '1785162186899312640-ha0z4tSleOVBiWdzdFBGGTD3Fqu16a'
DEFAULT_TWITTER_ACCESS_SECRET = 'wEWxTrehmw10sJrEspPtcX5IHyXRMTlmlb4i06ZPdID23'
TWITTER_BEARER_TOKEN = 'AAAAAAAAAAAAAAAAAAAAAKjMwAEAAAAAHgtI0k%2BcC3s%2Bpy%2BIp3zF1GmTtJw%3DjRXd5Qi43xnjrWOofqeVAjz9EHnVp4zAekTBmDqZ8FylRhwzv1'  # Replace with your actual bearer token

# Telegram bot token
TELEGRAM_TOKEN = '8048918660:AAEAhge8Y79AoNbHfFa_c0Ulm4zFt5E-Uww'

# Initialize the Telegram bot
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Set up Twitter authentication
auth = tweepy.OAuth1UserHandler(DEFAULT_TWITTER_API_KEY, DEFAULT_TWITTER_API_SECRET, DEFAULT_TWITTER_ACCESS_TOKEN, DEFAULT_TWITTER_ACCESS_SECRET)
twitter_api = tweepy.API(auth)

# Store user Twitter filters
user_filters = {}

# Command handler for /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Welcome to the Twitter Live Feed bot! Use /subscribe <keyword> to get live tweets. Use /usage to see Twitter API usage.")

# Command handler for /ping
@bot.message_handler(commands=['ping'])
def ping(message):
    bot.reply_to(message, "Pong!")

# Command handler for /subscribe
@bot.message_handler(commands=['subscribe'])
def subscribe(message):
    args = message.text.split()  # Get the command and parameters
    if len(args) == 2:
        keyword = args[1]
        user_id = message.chat.id
        
        # Store the filter for this user
        if user_id not in user_filters:
            user_filters[user_id] = []
        user_filters[user_id].append(keyword)
        
        # Add Twitter filtered stream rule
        add_filter_to_stream(keyword)
        
        bot.reply_to(message, f"You have subscribed to tweets containing: {keyword}")
    else:
        bot.reply_to(message, "Please provide a keyword to subscribe. Example: /subscribe cat")

# Function to add filter to Twitter stream
def add_filter_to_stream(keyword):
    url = "https://api.twitter.com/2/tweets/search/stream/rules"
    headers = {
        "Authorization": f"Bearer {TWITTER_BEARER_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "add": [{"value": keyword, "tag": f"Keyword: {keyword}"}]
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 201:
        logger.error(f"Error adding rule to stream: {response.text}")
    else:
        logger.info(f"Rule added to stream: {keyword}")

# Function to fetch API usage stats from Twitter
def fetch_twitter_usage():
    url = "https://api.twitter.com/2/usage/tweets"
    headers = {
        "Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        logger.error(f"Error fetching Twitter usage: {response.status_code}")
        return None

# Command handler for /usage
@bot.message_handler(commands=['usage'])
def usage(message):
    usage_data = fetch_twitter_usage()
    if usage_data:
        cap_reset_day = usage_data["data"]["cap_reset_day"]
        project_cap = usage_data["data"]["project_cap"]
        project_usage = usage_data["data"]["project_usage"]
        
        bot.reply_to(message, f"Twitter API Usage:\nProject Cap: {project_cap}\nUsage: {project_usage}\nCap Reset Day: {cap_reset_day}")
    else:
        bot.reply_to(message, "Error retrieving Twitter usage information.")

# Function to fetch tweets from Twitter stream
def fetch_tweets_from_stream():
    url = "https://api.twitter.com/2/tweets/search/stream"
    headers = {
        "Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"
    }
    
    while True:
        try:
            response = requests.get(url, headers=headers, stream=True)
            
            if response.status_code != 200:
                logger.error(f"Error connecting to Twitter stream: {response.text}")
                time.sleep(15)  # Wait before retrying
                continue

            # Stream tweets in real-time
            for line in response.iter_lines():
                if line:
                    tweet_data = json.loads(line)
                    tweet_text = tweet_data['data']['text']
                    tweet_author_id = tweet_data['data']['author_id']
                    tweet_id = tweet_data['data']['id']
                    
                    # Find users who are subscribed to this keyword
                    for user_id, filters in user_filters.items():
                        for keyword in filters:
                            if keyword.lower() in tweet_text.lower():
                                tweet_url = f"https://twitter.com/{tweet_author_id}/status/{tweet_id}"
                                bot.send_message(user_id, f"New tweet matching '{keyword}':\n{tweet_text}\n{tweet_url}")
        except Exception as e:
            logger.error(f"Error fetching tweets: {e}")
            time.sleep(15)  # Retry after a delay

# Run the Twitter stream fetching in a separate thread
def start_twitter_stream():
    twitter_stream_thread = threading.Thread(target=fetch_tweets_from_stream)
    twitter_stream_thread.start()

# Main function
if __name__ == '__main__':
    try:
        # Start the Twitter stream fetching
        start_twitter_stream()
        
        # Start the Telegram bot polling
        logger.info("Starting the bot...")
        bot.polling(none_stop=True, interval=0, timeout=60)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
