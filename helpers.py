import cloudscraper
from bs4 import BeautifulSoup
import time
import random


def extract_chapterlinks(html_content):
    chapter_links = []
    soup = BeautifulSoup(html_content, "html.parser")
    a_tags = soup.find_all("a", class_="item-content")
    for a_tag in a_tags:
        chapter_links.append("https://casetext.com/" + a_tag["href"])
    return chapter_links


def scrape_website(url):
    scraper = cloudscraper.create_scraper()  # Use a real browser User-Agent
    response = scraper.get(url)
    return response.text


def flatten_and_filter(nested_list):
    """
    Flattens a nested list and filters out empty elements.

    Args:
        nested_list (list): A potentially nested list with elements to be flattened.

    Returns:
        list: A flattened list with empty elements removed.
    """
    flat_list = []
    for sublist in nested_list:
        if isinstance(sublist, list):  # Check if the element is a list
            for item in sublist:
                if item:  # Check if the item is not empty
                    flat_list.append(item)
        elif sublist:  # If it's not a list and not empty, add it
            flat_list.append(sublist)

    # Remove any remaining empty elements
    return [item for item in flat_list if item]


def extract_part_links(chapter_links):
    """
    Extracts part links from a list of chapter links by applying scraping and extraction functions.

    Args:
        chapter_links (list): A list of chapter links to process.
        extract_function (function): A function to extract chapter links from scraped data.
        scrape_function (function): A function to scrape website data.

    Returns:
        list: A list of part links extracted from the chapter links.
    """
    part_links = []
    for link in chapter_links:
        part_links.append(extract_chapterlinks(scrape_website(link)))
        if random.choice([True, False]):
            time.sleep(random.uniform(1, 2))
    return part_links
