import signal
import sys
import logging
from flask import Flask, jsonify
import requests
from types import FrameType
from utils.logging import logger


import cloudscraper
# Flask app setup
app = Flask(__name__)


def scrape_website(url):
    scraper = cloudscraper.create_scraper()  # Use a real browser User-Agent
    response = scraper.get(url)
    return response.text




# Endpoint to fetch the URL and process it
@app.route("/fetch-url", methods=["GET"])
def fetch_url():
    """
    Fetches the URL and processes it.
    """
    try:
        # Simulate URL fetching (this can be replaced with an actual dynamic URL later)
        url = "https://casetext.com/statute/texas-codes/insurance-code"

        # Scrape the website
        response = scrape_website(url)

        # Write the response to a file
        with open("output.txt", "w") as f:
            f.write(response)

        # Return a JSON response with the data
        return jsonify({"message": "URL fetched and processed", "data": response}), 200

    except Exception as e:
        logger.error(f"Error in /fetch-url: {e}")
        return jsonify({"error": str(e)}), 500

# Graceful shutdown handler
def shutdown_handler(signal_int: int, frame: FrameType) -> None:
    logger.info(f"Caught Signal {signal.strsignal(signal_int)}")

    # Perform any necessary cleanup, if required (e.g., flushing logs)
    # Flush or any other shutdown tasks can be performed here if necessary

    # Safely exit program
    sys.exit(0)

if __name__ == "__main__":
    # Running application locally, outside of a Google Cloud Environment
    # handles Ctrl-C termination
    signal.signal(signal.SIGINT, shutdown_handler)

    app.run(host="localhost", port=8080, debug=True)
else:
    # handles Cloud Run container termination (SIGTERM)
    signal.signal(signal.SIGTERM, shutdown_handler)
