import feedparser
import requests
from bs4 import BeautifulSoup
import ssl
import datetime

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

def ingest_rss_feed(url, source_name):
    """Ingests and parses an RSS feed."""
    try:
        if hasattr(ssl, '_create_unverified_context'):
            ssl._create_default_https_context = ssl._create_unverified_context

        feed = feedparser.parse(url)

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

                print(f"Source: {source_name}")
                print(f"Title: {title}")
                print(f"Link: {link}")
                print(f"Published: {published_date}")

                # Get article content
                content = get_article_content(link)
                if content:
                    print("Article Content:")
                    print(content[:500] + "..." if len(content) > 500 else content) #Print only the first 500 characters
                else:
                    print("Could not retrieve article content.")

                print("-" * 40)
        else:
            print(f"No entries found in {source_name} feed.")

    except Exception as e:
        print(f"Error processing {source_name} feed: {e}")

# Main execution
if __name__ == "__main__":
    feeds = {
        "Yahoo Finance": "https://finance.yahoo.com/news/rssindex/", # Start with just Yahoo Finance as a start
    }

    for source, url in feeds.items():
        ingest_rss_feed(url, source)