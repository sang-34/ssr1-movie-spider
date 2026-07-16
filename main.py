import json
import logging
import os

from config import RESULT_DIR, SAVE_JSON, TOTAL_PAGE
from spider.cleaner import safe_filename
from spider.crawler import scrape_detail, scrape_index
from spider.parser import parse_detail, parse_index
from storage.mongo_storage import MongoStorage
from storage.redis_storage import RedisDeduper
from utils.logger import init_logger


def save_json(item):
    os.makedirs(RESULT_DIR, exist_ok=True)

    name = safe_filename(item.get("name"))
    data_path = os.path.join(RESULT_DIR, f"{name}.json")

    with open(data_path, "w", encoding="utf-8") as file:
        json.dump(item, file, ensure_ascii=False, indent=2)

    logging.info("JSON saved: %s", data_path)


def collect_detail_urls(deduper):
    detail_urls = []

    for page in range(1, TOTAL_PAGE + 1):
        index_html = scrape_index(page)
        if not index_html:
            continue

        for detail_url in parse_index(index_html):
            if deduper.is_crawled(detail_url):
                logging.info("already crawled, skip: %s", detail_url)
                continue

            if deduper.is_new_detail_url(detail_url):
                logging.info("new detail url found: %s", detail_url)
            else:
                logging.info("found before but not crawled, retry: %s", detail_url)

            detail_urls.append(detail_url)

    return detail_urls


def crawl_detail_and_save(detail_url, storage, deduper):
    detail_html = scrape_detail(detail_url)
    if not detail_html:
        return

    item = parse_detail(detail_url, detail_html)
    logging.info("parsed item: %s", item)

    storage.save(item)

    if SAVE_JSON:
        save_json(item)

    deduper.mark_crawled(detail_url)
    logging.info("marked crawled: %s", detail_url)


def main():
    init_logger()

    storage = MongoStorage()
    deduper = RedisDeduper()

    detail_urls = collect_detail_urls(deduper)
    logging.info("detail url count: %s", len(detail_urls))

    for detail_url in detail_urls:
        crawl_detail_and_save(detail_url, storage, deduper)


if __name__ == "__main__":
    main()