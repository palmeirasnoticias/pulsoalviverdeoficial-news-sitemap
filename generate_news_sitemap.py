import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime

FEED_URL = "https://pulsoalviverdeoficial.blogspot.com/feeds/posts/default?alt=rss"
PUBLICATION_NAME = "Pulso Alviverde"
LANGUAGE = "pt"
OUTPUT_FILE = "news-sitemap.xml"

NS_SITEMAP = "http://www.sitemaps.org/schemas/sitemap/0.9"
NS_NEWS = "http://www.google.com/schemas/sitemap-news/0.9"

ET.register_namespace("", NS_SITEMAP)
ET.register_namespace("news", NS_NEWS)

with urllib.request.urlopen(FEED_URL) as response:
    feed_data = response.read()

root_feed = ET.fromstring(feed_data)

urlset = ET.Element(f"{{{NS_SITEMAP}}}urlset")

now = datetime.now(timezone.utc)
cutoff = now - timedelta(days=2)

items = root_feed.findall("./channel/item")

for item in items:
    title_element = item.find("title")
    link_element = item.find("link")
    date_element = item.find("pubDate")

    if (
        title_element is None
        or link_element is None
        or date_element is None
        or not title_element.text
        or not link_element.text
        or not date_element.text
    ):
        continue

    title = title_element.text.strip()
    link = link_element.text.strip()

    try:
        publication_date = parsedate_to_datetime(date_element.text)

        if publication_date.tzinfo is None:
            publication_date = publication_date.replace(tzinfo=timezone.utc)

        publication_date = publication_date.astimezone(timezone.utc)

    except Exception:
        continue

    if publication_date < cutoff:
        continue

    url = ET.SubElement(urlset, f"{{{NS_SITEMAP}}}url")

    loc = ET.SubElement(url, f"{{{NS_SITEMAP}}}loc")
    loc.text = link

    news = ET.SubElement(url, f"{{{NS_NEWS}}}news")

    publication = ET.SubElement(news, f"{{{NS_NEWS}}}publication")

    name = ET.SubElement(publication, f"{{{NS_NEWS}}}name")
    name.text = PUBLICATION_NAME

    language = ET.SubElement(publication, f"{{{NS_NEWS}}}language")
    language.text = LANGUAGE

    news_date = ET.SubElement(news, f"{{{NS_NEWS}}}publication_date")
    news_date.text = publication_date.strftime("%Y-%m-%dT%H:%M:%SZ")

    news_title = ET.SubElement(news, f"{{{NS_NEWS}}}title")
    news_title.text = title

tree = ET.ElementTree(urlset)

ET.indent(tree, space="  ")

tree.write(
    OUTPUT_FILE,
    encoding="utf-8",
    xml_declaration=True
)

print(f"Google News sitemap generated successfully: {OUTPUT_FILE}")
