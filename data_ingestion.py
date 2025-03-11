"""
This script ingests and stores the content from a list of RSS feeds. This is the beginning of the
data pipeline, where the extracted article contents will be sent off for sentiment analysis.
"""
import ssl
import re
import datetime
from dataclasses import dataclass
import feedparser
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
# import pandas as pd

# ANSI color codes for colored terminal output
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
MAGENTA = '\033[95m'
CYAN = '\033[96m'
RESET = '\033[0m'

@dataclass
class RSSArticle():
    """Data class to store information about an RSS article."""
    source: str
    title: str
    link: str
    published: str
    content: str = None
    sentiment: tuple[str, float] = (None, None)

def extract_rate_limit_warning(rss_summary):
    """
    Extracts a rate limit warning from a given text, focusing on key phrases.

    Args:
        text: The input text to search.

    Returns:
        The extracted warning message, or None if not found.
    """
    patterns = [
        r"(rate limit exceeded)",
        r"(access limit exceeded)",
        r"(too many requests)",
        r"(request limit reached)",
        r"(exceeded page access rate limit)",
        r"(exceeded request limit)",
        r"(limit reached)",
        r"(rate limited)",
        r"(too many connections)",
        r"(blocked due to excessive requests)"
    ]

    for pattern in patterns:
        match = re.search(pattern, rss_summary, re.IGNORECASE)
        if match:
            lines = rss_summary.splitlines()
            matched_line_number = -1
            for i, line in enumerate(lines):
                if re.search(pattern, line, re.IGNORECASE): #corrected line
                    matched_line_number = i
                    break

            if matched_line_number != -1:
                result = lines[matched_line_number].strip()
                if matched_line_number + 1 < len(lines):
                    next_line = lines[matched_line_number + 1].strip()
                    if next_line:  # Check if the next line has content
                        result += "\n" + next_line
                return result
    return None

def get_article_content(article_url):
    """Retrieves and parses the content of an article."""
    try:
        response = requests.get(article_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract article content based on common HTML tags, append them together
        paragraphs = soup.find_all('p')
        content = '\n'.join([p.get_text() for p in paragraphs])

        return content
    except (ssl.SSLError, requests.exceptions.RequestException) as e:
        tqdm.write(f"{RED}Error fetching article content: {RESET}{e}")
        return None
    except Exception as e: # pylint: disable=broad-except
        tqdm.write(f"{RED}Error parsing article content: {RESET}{e}")
        return None

def ingest_rss_feed(source_url, source_name) -> list[RSSArticle]:
    """Ingests and parses an RSS feed."""

    article_content: list[RSSArticle] = []

    try:
        if hasattr(ssl, '_create_unverified_context'):
            ssl._create_default_https_context = ssl._create_unverified_context # pylint: disable=protected-access

        print (f"{MAGENTA}Attempting to parse feed: {RESET}", source_url)
        feed = feedparser.parse(source_url)

        if feed.entries:
            for entry in tqdm(feed.entries, desc=f"Processing {source_name} feed"):
                title = entry.title
                link = entry.link
                published = entry.published if hasattr(entry, 'published') else "No Published Date"

                # Convert published date to a datetime object (if possible)
                try:
                    published_date = datetime.datetime.strptime(published,
                                                                "%a, %d %b %Y %H:%M:%S %z")
                except ValueError:
                    try:
                        published_date = datetime.datetime.strptime(published,
                                                                    "%Y-%m-%dT%H:%M:%SZ")
                    except ValueError:
                        published_date = published

                # Get article content
                content = get_article_content(link)
                article_content.append(RSSArticle(source_name, title, link,
                                                  published_date, content))

        else:
            warning_text = extract_rate_limit_warning(feed.feed.summary)

            if warning_text:
                tqdm.write(f"{YELLOW}No entries found in {source_name} feed: {RESET}{warning_text}")
            else:
                tqdm.write(f"{YELLOW}No entries found in {source_name} feed{RESET}")

        return article_content

    except Exception as e: # pylint: disable=broad-except
        tqdm.write(f"{RED}Error processing {source_name} feed: {RESET}{e}")
        return []

# Main execution
if __name__ == "__main__":
    feeds = {
        # Start with just Yahoo Finance as a start
        "Yahoo Finance": "https://finance.yahoo.com/news/rssindex/",
        # PRLog is a free RSS feed (multiple topics to choose from), but rate limited
        "PRLog": "https://prlog.org/news/ind/business/rss.xml",
    }

    for source, url in feeds.items():
        ingest_rss_feed(url, source)
