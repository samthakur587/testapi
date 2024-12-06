import signal
import sys
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from types import FrameType
import requests

# FastAPI app setup
app = FastAPI()

from utils.logging import logger

# Function to simulate scraping the website
def scrape_website(url: str) -> str:
    try:
        # For demonstration purposes, we use a simple GET request
        response = requests.get(url)
        
        if response.status_code == 200:
            return response.text  # Returning the HTML content as the response
        else:
            return f"Failed to fetch the website, status code: {response.status_code}"
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching the website: {e}")
        return f"Error: {str(e)}"

# Endpoint to fetch the URL and process it
@app.get("/fetch-url")
async def fetch_url():
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
        return JSONResponse(content={"message": "URL fetched and processed", "data": response}, status_code=200)

    except Exception as e:
        logger.error(f"Error in /fetch-url: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

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
