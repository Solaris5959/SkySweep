import feedparser
import requests
from bs4 import BeautifulSoup
import ssl
import datetime
import pandas as pd
from dataclasses import dataclass

@dataclass
class rss_article():
    Source: str
    Title: str
    Link: str
    Published: str
    Content: str = None
    Sentiment: tuple[str, float] = (None, None)


def get_article_content(url):
    """Retrieves and parses the content of an article."""
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract article content based on common HTML tags (adjust as needed)
        paragraphs = soup.find_all('p')
        content = '\n'.join([p.get_text() for p in paragraphs])

        return content

    except requests.exceptions.RequestException as e:
        print(f"Error fetching article content: {e}")
        return None
    except Exception as e:
        print(f"Error parsing article content: {e}")
        return None

# TODO: Add loading display for RSS-Feed Ingestion
def ingest_rss_feed(url, source_name) -> list[rss_article]:
    article_content: list[rss_article] = []
    """Ingests and parses an RSS feed."""
    try:
        if hasattr(ssl, '_create_unverified_context'):
            ssl._create_default_https_context = ssl._create_unverified_context

        print ("Attempting to parse feed: ", url)
        feed = feedparser.parse(url)
        if (url == "https://prlog.org/news/ind/business/rss.xml"):
            print("Feed: ", feed)

        if feed.entries:
            for entry in feed.entries:
                title = entry.title
                link = entry.link
                published = entry.published if hasattr(entry, 'published') else "No Published Date"

                # Convert published date to a datetime object (if possible)
                try:
                    published_date = datetime.datetime.strptime(published, "%a, %d %b %Y %H:%M:%S %z")
                except ValueError:
                    try:
                        published_date = datetime.datetime.strptime(published, "%Y-%m-%dT%H:%M:%SZ")
                    except ValueError:
                        published_date = published

                # Get article content
                content = get_article_content(link)
                article_content.append(rss_article(source_name, title, link, published_date, content))

        else:
            print(f"No entries found in {source_name} feed.")

        for article in article_content:
            print(article.Title)
        return article_content

    except Exception as e:
        print(f"Error processing {source_name} feed: {e}")

# Main execution
if __name__ == "__main__":
    feeds = {
        "Yahoo Finance": "https://finance.yahoo.com/news/rssindex/", # Start with just Yahoo Finance as a start
        "PRLOG": "https://prlog.org/news/ind/business/rss.xml", # PRLog is a free RSS feed (multiple topics to choose from), but rate limited
    }

    for source, url in feeds.items():
        ingest_rss_feed(url, source)