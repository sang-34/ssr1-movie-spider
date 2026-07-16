import html
import re


def clean_text(value):
    if value is None:
        return None

    value = html.unescape(value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def clean_date(value):
    value = clean_text(value)
    if not value:
        return None

    match = re.search(r"\d{4}-\d{2}-\d{2}", value)
    return match.group() if match else None


def clean_score(value):
    value = clean_text(value)
    if not value:
        return None

    match = re.search(r"\d+(\.\d+)?", value)
    return float(match.group()) if match else None


def safe_filename(value):
    value = clean_text(value) or "unknown"
    return re.sub(r'[\\/:*?"<>|]', " ", value)