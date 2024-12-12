import signal, cloudscraper
import sys,os
import logging
from flask import Flask, jsonify, request
import requests
from types import FrameType
from utils.logging import logger
from helpers import extract_chapterlinks, flatten_and_filter, extract_part_links
import pickle
from document_helpers import process_html_documents
import datetime
from google.cloud import storage
from dotenv import load_dotenv
from celery import Celery
from tor import renew_tor_ip

load_dotenv()

BUCKET_NAME = 'case-code-pipeline'

# celery = Celery('app', broker='redis://localhost:6379/0') 


# Flask app setup
app = Flask(__name__)


def scrape_website(url):
    scraper = cloudscraper.create_scraper()  # Use a real browser User-Agent
    response = scraper.get(url)
    return response.text

# @celery.task
def process_pipeline(url, html_content):
    try:
        chapter_links = extract_chapterlinks(html_content)

        # Step 2: Extract and process links
        part_links = flatten_and_filter(extract_part_links(chapter_links))
        subpart_links = flatten_and_filter(extract_part_links(part_links))
        section_links = flatten_and_filter(extract_part_links(subpart_links))

        file_name = f"sections_list_{url.replace('://', '_').replace('/', '_')}.pkl"
        with open(file_name, "wb") as file:
            pickle.dump(section_links, file)

        logger.info(f"Section links saved to {file_name}")

        # Step 4: Process sections
        processed_docs = process_html_documents(
                section_links,
                f"sections_{url.replace('://', '_').replace('/', '_')}.json",
                chunk_size=3,
                sleep_min=1,
                sleep_max=6,
            )
        logger.info(f"Processing completed for URL: {url}")

        return processed_docs
    except Exception as e:
        logger.error(f"Error processing task: {e}")
        return None



# @celery.task
def save_to_gcp_bucket(bucket_name, destination_blob_name, data):
    """Uploads data to the specified GCP bucket."""
    client = storage.Client("compfox-367313-8c81066d05ec.json")
    bucket = client.bucket(bucket_name)

    # Get the current date
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    # Create a folder path with the current date
    folder_path = f"{current_date}/{destination_blob_name}"

    blob = bucket.blob(folder_path)  # Use the folder path
    blob.upload_from_string(data) 


# Endpoint to fetch the URL and process it
@app.route("/fetch-url", methods=["GET"])
def fetch_url():
    """
    Fetches the URL and processes it.
    """
    try:
        # Accept URL as a query parameter
        url = request.args.get("url")
        
        if not url:
            return jsonify({"error": "URL parameter is required"}), 400

        # Scrape the website
        response = scrape_website(url)

        # Write the response to a file
        with open("output2.html", "w") as f:
            f.write(response)
        
        # Process the pipeline
        # response = process_pipeline(url, response)
        ### cOMMENTING TO FIRST TEST THE SCRAPER AND DB CONNECTION

        # Save processed data to GCP bucket
         # Specify your bucket name
        task = save_to_gcp_bucket(bucket_name=BUCKET_NAME, destination_blob_name=f"processed_{url.replace('://', '_').replace('/', '_')}.json", data=response)
        # task = save_to_gcp_bucket.apply_async(args=[BUCKET_NAME, f"processed_{url.replace('://', '_').replace('/', '_')}.json", response])
        return jsonify({"message": "URL fetched and processed", "task_id": task.id}), 200

    except Exception as e:
        logger.error(f"Error in /fetch-url: {e}")
        return jsonify({"error": str(e)}), 500

 # Upload the processed data as a string

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
