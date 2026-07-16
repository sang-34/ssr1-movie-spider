BASE_URL = "https://ssr1.scrape.center/"
TOTAL_PAGE = 10
RESULT_DIR = "results"
TIMEOUT = 10

SAVE_JSON = False

MONGO_URI = "mongodb://127.0.0.1:27017"
MONGO_DATABASE  = "spider_center"
MONGO_COLLECTION = "ssr1_movies1"

REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 1
REDIS_PASSWORD = "foobared"

REDIS_DETAIL_URLS_KEY = "ssr1:movie:detail_urls"
REDIS_CRAWLED_URLS_KEY = "ssr1:movie:crawled_urls"

MAX_RETRY = 3
MIN_SLEEP = 0.5
MAX_SLEEP = 1.5

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