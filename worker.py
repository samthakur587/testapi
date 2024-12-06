import asyncio
import aiofiles
import pickle
import json
from google.cloud import pubsub_v1
import logging
from helpers import (
    scrape_website,
    extract_chapterlinks,
    flatten_and_filter,
    extract_part_links,
)
from document_helpers import process_html_documents

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

publisher = pubsub_v1.PublisherClient.from_service_account_json("compfox-367313-8c81066d05ec.json")
PUBSUB_TOPIC = "projects/compfox-367313/topics/scrape-tasks"

async def process_task(data):
    """
    Process a scraping task: scrape the URL and process sections.
    """
    try:
        url = data.get("url")
        if not url:
            raise ValueError("URL is required in task data")

        logger.info(f"Starting processing for URL: {url}")

        # Step 1: Scrape website content
        html_content = await scrape_website(url)
        chapter_links = extract_chapterlinks(html_content)

        # Step 2: Extract and process links
        part_links = await flatten_and_filter(extract_part_links(chapter_links))
        subpart_links = await flatten_and_filter(extract_part_links(part_links))
        section_links = await flatten_and_filter(extract_part_links(subpart_links))

        # Step 3: Serialize section links to a file
        file_name = f"sections_list_{url.replace('://', '_').replace('/', '_')}.pkl"
        async with aiofiles.open(file_name, "wb") as file:
            await file.write(pickle.dumps(section_links))

        logger.info(f"Section links saved to {file_name}")

        # Step 4: Process sections
        processed_docs = await process_html_documents(
            section_links,
            f"sections_{url.replace('://', '_').replace('/', '_')}.json",
            chunk_size=3,
            sleep_min=2,
            sleep_max=6,
        )
        logger.info(f"Processing completed for URL: {url}")

        return processed_docs
    except Exception as e:
        logger.error(f"Error processing task: {e}")
        return None


def callback(message):
    """
    Pub/Sub callback for processing a task.
    """
    try:
        task_data = json.loads(message.data.decode("utf-8"))
        asyncio.run(process_task(task_data))
        message.ack()  # Acknowledge the message
        logger.info("Task processed and message acknowledged.")
    except Exception as e:
        logger.error(f"Error in message callback: {e}")
