import json
import logging
import os
from urllib.parse import urlparse

from config import RESULT_DIR, SAVE_JSON, TOTAL_PAGE
from spider.cleaner import safe_filename
from spider.crawler import scrape_detail, scrape_index
from spider.parser import parse_detail, parse_index
from storage.mongo_storage import MongoStorage
from storage.redis_storage import RedisDeduper
from utils.logger import init_logger

logger = logging.getLogger(__name__)


def save_json(item):
    os.makedirs(RESULT_DIR, exist_ok=True)

    name = safe_filename(item.get("name"))
    data_path = os.path.join(RESULT_DIR, f"{name}.json")

    with open(data_path, "w", encoding="utf-8") as file:
        json.dump(item, file, ensure_ascii=False, indent=2)

    logging.info("JSON saved: %s", data_path)


def collect_detail_urls(deduper, stats):
    detail_urls = []

    for page in range(1, TOTAL_PAGE + 1):
        logger.info("start crawling index page: %s", page)

        index_html = scrape_index(page)
        if not index_html:
            logger.warning("index page request failed: %s", page)
            stats["failed_index_pages"] += 1
            continue

        page_detail_urls = list(parse_index(index_html))
        logger.info(
            "index page %s extracted detail urls: %s",
            page,
            len(page_detail_urls),
        )

        stats["total_detail_urls"] += len(page_detail_urls)

        for detail_url in page_detail_urls:
            if deduper.is_crawled(detail_url):
                stats["skipped_crawled_urls"] += 1
                logging.info("already crawled, skip: %s", detail_url)
                continue

            if deduper.is_new_detail_url(detail_url):
                logging.info("new detail url found: %s", detail_url)
            else:
                logging.info("found before but not crawled, retry: %s", detail_url)

            detail_urls.append(detail_url)

    logger.info("pending detail urls count: %s", len(detail_urls))
    return detail_urls


def is_valid_item(item):
    if not isinstance(item, dict):
        logging.warning("invalid item type: %s", item)
        return False

    url = item.get("url")
    name = item.get("name")
    score = item.get("score")
    drama = item.get("drama")

    parsed_url = urlparse(url or "")
    if not parsed_url.scheme or not parsed_url.netloc:
        logging.warning("invalid item url: %s", item)
        return False

    if not name:
        logging.warning("invalid item name: %s", item)
        return False

    if score is None:
        logging.warning("invalid item score: %s", item)
        return False

    if not drama:
        logging.warning("invalid item drama: %s", item)
        return False

    return True


def crawl_detail_and_save(detail_url, storage, deduper, stats):
    detail_html = scrape_detail(detail_url)
    if not detail_html:
        stats["failed_detail_urls"] += 1
        logger.warning("detail page request failed: %s", detail_url)
        return

    item = parse_detail(detail_url, detail_html)

    if not is_valid_item(item):
        stats["parse_failed_items"] += 1
        logger.warning("invalid item, skip save and mark crawled: %s", detail_url)
        return

    save_success = storage.save(item)
    if not save_success:
        stats["save_failed_items"] += 1
        logger.warning("save failed, skip mark crawled: %s", detail_url)
        return

    stats["saved_items"] += 1
    logger.info("movie saved successfully: %s", item.get("name"))

    if SAVE_JSON:
        save_json(item)

    deduper.mark_crawled(detail_url)
    logging.info("marked crawled: %s", detail_url)


def main():
    init_logger()

    stats = {
        "total_detail_urls": 0,
        "skipped_crawled_urls": 0,
        "failed_index_pages": 0,
        "failed_detail_urls": 0,
        "parse_failed_items": 0,
        "save_failed_items": 0,
        "saved_items": 0,
    }

    logger.info("ssr1 movie spider started")

    storage = MongoStorage()
    deduper = RedisDeduper()

    detail_urls = collect_detail_urls(deduper, stats)

    for detail_url in detail_urls:
        crawl_detail_and_save(detail_url, storage, deduper, stats)

    logger.info("ssr1 movie spider finished")
    logger.info("total detail urls extracted: %s", stats["total_detail_urls"])
    logger.info("skipped crawled urls: %s", stats["skipped_crawled_urls"])
    logger.info("failed index pages: %s", stats["failed_index_pages"])
    logger.info("failed detail urls: %s", stats["failed_detail_urls"])
    logger.info("parse failed items: %s", stats["parse_failed_items"])
    logger.info("save failed items: %s", stats["save_failed_items"])
    logger.info("saved items: %s", stats["saved_items"])


if __name__ == "__main__":
    main()