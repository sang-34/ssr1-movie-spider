import requests
import logging
import re
from urllib.parse import urljoin
import json
from os import makedirs
from os.path import exists
import multiprocessing

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

BASE_URL = "https://ssr1.scrape.center/"
TOTAL_PAGE = 10

RESULT_DIR = "results"
makedirs(RESULT_DIR, exist_ok=True)

headers = {
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

# 爬取页面
def scrape_page(url):
    logging.info("scraping %s...", url)
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        logging.info("get invalid status code %s while scraping %s", response.status_code, url)
    except requests.RequestException:
        logging.info("error occurred while scraping %s", url, exc_info=True)

# 爬取列表页
def scrape_index(page):
    index_url = f"{BASE_URL}page/{page}"
    return scrape_page(index_url)

# 解析列表页 得到每部电影详细的 URL
def parse_index(html):
    pattern = re.compile(r'<a.*?href="(.*?)".*?name">')
    items = re.findall(pattern, html)
    for item in items:
        detail_url = urljoin(BASE_URL, item)
        logging.info("get detail url %s", detail_url)
        yield detail_url

# 爬取详情页
def scrape_detail(url):
    return scrape_page(url)

# 解析详情页 提取电影的名称 封面 类别 上映时间 评分 剧情简介等内容
def parse_detail(html):
    cover_pattern = re.compile('class="item.*?<img.*?src="(.*?)".*?cover">', re.S)
    name_pattern = re.compile('<h2.*?>(.*?)</h2>', re.S)
    categories_pattern = re.compile('<button.*?category.*?span>(.*?)</span>.*?</button>', re.S)
    publish_at_pattern = re.compile('(\d{4}-\d{2}-\d{2})\s+上映', re.S)
    drama_pattern = re.compile('<div.*?class="drama".*?<p.*?>(.*?)</p>', re.S)
    score_pattern = re.compile('<p.*?class="score.*?>(.*?)</p>', re.S)

    cover_match = re.search(cover_pattern, html)
    cover = cover_match.group(1).strip() if cover_match else None
    name_match = re.search(name_pattern, html)
    name = name_match.group(1).strip() if name_match else None
    categories_match = re.findall(categories_pattern, html)
    categories = categories_match if categories_match else []
    publish_at_match = re.search(publish_at_pattern, html)
    publish_at = publish_at_match.group(1).strip() if publish_at_match else None
    drama_match = re.search(drama_pattern, html)
    drama = drama_match.group(1).strip() if drama_match else None
    scores_match = re.search(score_pattern, html)
    scores = float(scores_match.group(1).strip()) if scores_match else None

    return {
        "cover": cover,
        "name": name,
        "categories": categories,
        "publish_at": publish_at,
        "drama": drama,
        "scores": scores
    }

# 保存数据
def save_data(data):
    name = data.get("name")
    name = re.sub(r":", " ", name)
    data_path = f"{RESULT_DIR}/{name}.json"
    json.dump(data, open(data_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

def main(page):
    index_html = scrape_index(page)
    detail_urls = parse_index(index_html)
    for detail_url in detail_urls:
        detail_html = scrape_detail(detail_url)
        data = parse_detail(detail_html)
        logging.info("get detail data %s", data)
        logging.info("saving data to json file")
        save_data(data)
        logging.info("data saved successfully")

if __name__ == "__main__":
    pool = multiprocessing.Pool()
    pages = range(1, TOTAL_PAGE + 1)
    pool.map(main, pages)
    pool.close()
    pool.join()
































































