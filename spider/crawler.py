import logging
from urllib.parse import urljoin

import requests

from config import BASE_URL, HEADERS, TIMEOUT


def scrape_page(url):
    logging.info("scraping %s", url)

    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        if response.status_code == 200:
            return response.text

        logging.warning(
            "invalid status code %s while scraping %s",
            response.status_code,
            url,
        )
    except requests.RequestException:
        logging.exception("error occurred while scraping %s", url)

    return None


def scrape_index(page):
    index_url = urljoin(BASE_URL, f"page/{page}")
    return scrape_page(index_url)


def scrape_detail(url):
    return scrape_page(url)