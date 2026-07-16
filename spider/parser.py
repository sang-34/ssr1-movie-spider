from datetime import datetime
from urllib.parse import urljoin

from parsel import Selector

from config import BASE_URL
from spider.cleaner import clean_date, clean_score, clean_text


def parse_index(html_text):
    selector = Selector(html_text)
    hrefs = selector.css("a.name::attr(href)").getall()

    for href in hrefs:
        yield urljoin(BASE_URL, href)


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
        "name": clean_text(name),
        "cover": clean_text(cover),
        "categories": [clean_text(item) for item in categories if clean_text(item)],
        "published_at": clean_date(page_text),
        "score": clean_score(score),
        "drama": clean_text(drama),
        "created_at": now,
        "updated_at": now,
    }