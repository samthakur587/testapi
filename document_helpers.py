import time
import random
import json
from langchain_community.document_loaders import AsyncHtmlLoader
from langchain_community.document_transformers import Html2TextTransformer


def process_html_documents(
    final_content_list, output_file, chunk_size=3, sleep_min=2, sleep_max=6
):
    """
    Processes a list of URLs, splits them into chunks, fetches and transforms the HTML content,
    and saves the results as JSON to a file.

    Args:
        final_content_list (list): List of URLs to process.
        output_file (str): Path to the output JSON file.
        chunk_size (int): Maximum number of URLs to process in one chunk. Default is 3.
        sleep_min (int): Minimum sleep time between chunks. Default is 2 seconds.
        sleep_max (int): Maximum sleep time between chunks. Default is 6 seconds.

    Returns:
        list: A list of transformed documents.
    """

    # Function to split the list into chunks
    def chunk_list(lst, chunk_size):
        for i in range(0, len(lst), chunk_size):
            yield lst[i : i + chunk_size]

    # Initialize the transformer
    html2text = Html2TextTransformer()
    all_docs_transformed = []

    # Split the list into chunks
    chunked_lists = list(chunk_list(final_content_list, chunk_size))

    # Loop through each chunk
    for chunk in chunked_lists:
        # Randomize sleep time for each chunk
        sleep_time = random.uniform(sleep_min, sleep_max)

        # Load documents from the current chunk
        loader = AsyncHtmlLoader(chunk)
        docs = loader.load()

        # Transform the documents
        docs_transformed = html2text.transform_documents(docs)

        # Add transformed documents to the final list
        all_docs_transformed.extend(docs_transformed)

        # Sleep to avoid overloading resources
        time.sleep(sleep_time)

    # Write the transformed documents to the output file
    with open(output_file, "a") as f:
        json.dump([doc.to_json() for doc in all_docs_transformed], f, indent=4)

    return all_docs_transformed


# # Example Usage:
# final_content_list = [
#     "http://example.com/1",
#     "http://example.com/2",
#     "http://example.com/3",
#     "http://example.com/4",
# ]
# output_file = "/content/drive/MyDrive/pipeline/sections_insurence_code.json"

# all_transformed_docs = process_html_documents(
#     final_content_list, output_file, chunk_size=3, sleep_min=2, sleep_max=6
# )
