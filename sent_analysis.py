"""
This script currently does sentiment analysis on the titles of the articles.
The goal is to expand this to analyze the content of the articles as well and adding natural
language processing (NLP) capabilities among other things.
"""
from transformers import pipeline
import yfinance as yf
from data_ingestion import ingest_rss_feed, RSSArticle
#import pandas as pd

# ANSI color codes for colored terminal output
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
MAGENTA = '\033[95m'
CYAN = '\033[96m'
RESET = '\033[0m'

MODEL = "yiyanghkust/finbert-tone"
TEXT_TASK = "text-classification"
NER_TASK = "ner"

class ModelAnalysis():
    """ A class to analyze the sentiment of a list of articles using a pre-trained model. """
    def __init__(self, model, task):
        self.model = model
        self.task = task
        self.sentiment_pipeline = pipeline(task=task, model=model)

    def run(self, article_list: list[RSSArticle]) -> None:
        """ Runs the sentiment analysis on a list of articles. """
        titles = [article.title for article in article_list]
        results = self.sentiment_pipeline(titles)

        if self.task is NER_TASK:
            for entity in results:
                print(entity)

        if self.task is TEXT_TASK:
            for title, sentiment in zip(titles, results):
                index = next(i for i, a in enumerate(article_list) if a.title == title)
                article_list[index].sentiment = (sentiment['label'], sentiment['score'])
                print(f"'{title}' --> {sentiment['label']} ({sentiment['score']:.2f})")

        return article_list


def fetch_hist_ticker(ticker: str):
    """ Fetches historical stock data for a given ticker. """
    ticker = 'TSLA'
    df = yf.download(ticker, period="6mo", interval="1d")

    # Append mock sentiment scores (in production, you'd batch-process sentiment)
    df['Sentiment'] = [0.98 if i % 2 == 0 else 0.3 for i in range(len(df))]

    print(df.tail())

# Main execution
if __name__ == "__main__":
    feeds = {
        # Start with just Yahoo Finance as a start
        "Yahoo Finance": "https://finance.yahoo.com/news/rssindex/",
        # PRLog is a free RSS feed (multiple topics to choose from), but rate limited
        "PRLog": "https://prlog.org/news/ind/business/rss.xml",
    }

    sent = ModelAnalysis("dbmdz/bert-large-cased-finetuned-conll03-english", NER_TASK)

    for source, url in feeds.items():
        articles = ingest_rss_feed(url, source)
        if articles:
            sent.run(articles)
        else:
            print(f"{RED}No articles found for {source}{RESET}")
