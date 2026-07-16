import logging
import random
import time
from urllib.parse import urljoin

import requests

from config import BASE_URL, HEADERS, MAX_RETRY, MAX_SLEEP, MIN_SLEEP, TIMEOUT


def scrape_page(url):
    for retry_count in range(1, MAX_RETRY + 1):
        logging.info("scraping %s, retry %s/%s", url, retry_count, MAX_RETRY)

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

        sleep_random()

    logging.error("scraping failed after %s retries: %s", MAX_RETRY, url)
    return None


def sleep_random():
    sleep_seconds = random.uniform(MIN_SLEEP, MAX_SLEEP)
    time.sleep(sleep_seconds)


def scrape_index(page):
    index_url = urljoin(BASE_URL, f"page/{page}")
    return scrape_page(index_url)


def scrape_detail(url):
    return scrape_page(url)