import logging
import json
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
# from google.cloud import pubsub_v1

# FastAPI app setup
app = FastAPI()

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pub/Sub Publisher and Subscriber setup
# publisher = pubsub_v1.PublisherClient.from_service_account_json("compfox-367313-8c81066d05ec.json")
# subscriber = pubsub_v1.SubscriberClient.from_service_account_json("compfox-367313-8c81066d05ec.json")

# PUBSUB_TOPIC = "projects/compfox-367313/topics/scrape-tasks"
# PUBSUB_SUBSCRIPTION = "projects/compfox-367313/subscriptions/scrape-tasks-subscription"

import cloudscraper
def scrape_website(url):
    scraper = cloudscraper.create_scraper()  # Use a real browser User-Agent
    response = scraper.get(url)
    return response.text


# Endpoint to fetch URL from Pub/Sub (subscribe to messages)
@app.get("/fetch-url")
async def fetch_url():
    """
    Fetches the URL message from Pub/Sub.
    """
    try:
    #     # Pull a message from Pub/Sub subscription
    #     response = subscriber.pull(
    #         subscription=PUBSUB_SUBSCRIPTION,
    #         max_messages=1
    #     )
        
    #     if len(response.received_messages) == 0:
    #         return JSONResponse(content={"message": "No messages in the queue"}, status_code=200)

    #     # Extract the message (URL) from the Pub/Sub message
    #     pubsub_message = response.received_messages[0]
    #     message_data = json.loads(pubsub_message.message.data.decode("utf-8"))
    #     url = message_data.get("url")
        
        # Acknowledge the message
        # subscriber.acknowledge(
        #     subscription=PUBSUB_SUBSCRIPTION,
        #     ack_ids=[pubsub_message.ack_id]
        # )
        response = scrape_website(url="https://casetext.com/statute/texas-codes/insurance-code")

        with open("output.txt", "w") as f:
            f.write(response)
        
        return JSONResponse(content={"message": "URL fetched and processed", "data":response}, status_code=200)

    except Exception as e:
        logger.error(f"Error in /fetch-url: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)
