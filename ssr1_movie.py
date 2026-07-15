import os
from datetime import datetime
import requests
import logging
import html
import re
from urllib.parse import urljoin
import json
import multiprocessing
from parsel import Selector

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

BASE_URL = "https://ssr1.scrape.center/"
TOTAL_PAGE = 10
RESULT_DIR = "results"
TIMEOUT = 10

HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0',
    'sec-ch-ua': '"Microsoft Edge";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}


def clean_text(value):
    """清洗空白字符串和实体"""
    if value is None:
        return None

    value = html.unescape(value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def clean_date(value):
    """利用正则从文本中提取日期"""
    value = clean_text(value)
    if value is None:
        return None

    match = re.search(r"\d{4}-\d{2}-\d{2}", value)
    return match.group() if match else None


def clean_score(value):
    """利用正则提取分数, 并转成 float"""
    value = clean_text(value)
    if value is None:
        return None

    match = re.search(r"\d+(\.\d+)?", value)
    return float(match.group()) if match else None


def safe_filename(value):
    """清洗文件名中的非法符号"""
    value = clean_text(value) or "unknown"
    return re.sub(r'[\\/:*?"<>|]', " ", value)


# 爬取页面
def scrape_page(url):
    logging.info("scraping %s...", url)

    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        if response.status_code == 200:
            return response.text

        logging.warning("get invalid status code %s while scraping %s", response.status_code, url)
    except requests.RequestException:
        logging.exception("error occurred while scraping %s", url, exc_info=True)

    return None


# 爬取列表页
def scrape_index(page):
    index_url = urljoin(BASE_URL, f"page/{page}")
    return scrape_page(index_url)


# 解析列表页 得到每部电影详细的 URL
def parse_index(html_text):
    """使用 parsel 提取详情页 url"""
    selector = Selector(html_text)
    hrefs = selector.css("a.name::attr(href)").getall()

    for href in hrefs:
        yield urljoin(BASE_URL, href)


# 爬取详情页
def scrape_detail(url):
    return scrape_page(url)


# 解析详情页 提取电影的名称 封面 类别 上映时间 评分 剧情简介等内容
def parse_detail(url, html_text):
    selector = Selector(html_text)
    page_text = selector.xpath("string(.)").get()

    cover = selector.css("img.cover::attr(src)").get()
    name = selector.css("h2::text").get()
    categories = selector.css("button.category span::text").getall()
    drama = selector.css(".drama p::text").get()
    score = selector.css(".score::text").get()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return {
        "url": url,
        "name": name,
        "cover": cover,
        "categories": [clean_text(item) for item in categories if clean_text(item)],
        "publish_at": clean_date(page_text),
        "score": clean_score(score),
        "drama": clean_text(drama),
        "created_at": now,
        "updated_at": now,
    }


# 保存数据
def save_data(item):
    os.makedirs(RESULT_DIR, exist_ok=True)

    name = safe_filename(item.get("name"))
    data_path = os.path.join(RESULT_DIR, f"{name}.json")

    with open(data_path, "w", encoding="utf-8") as file:
        json.dump(item, file, ensure_ascii=False, indent=2)

    logging.info("data saved successfully：%s", data_path)


def main():
    for page in range(1, TOTAL_PAGE + 1):
        index_html = scrape_index(page)
        if not index_html:
            continue

        detail_urls = parse_index(index_html)

        for detail_url in detail_urls:
            detail_html = scrape_detail(detail_url)
            if not detail_html:
                continue

            item = parse_detail(detail_url, detail_html)
            logging.info("scraping %s", item)

            save_data(item)


if __name__ == "__main__":
    main()
































































