from transformers import pipeline
import yfinance as yf
import pandas as pd
from data_ingestion import *

MODEL = "yiyanghkust/finbert-tone"
TEXT_TASK = "text-classification"
NER_TASK = "ner"

class ModelAnalysis():
    def __init__(self, model, task):
        self.model = model
        self.task = task
        self.sentiment_pipeline = pipeline(task=task, model=model)
        
    def run(self, articles: list[rss_article]) -> None:
        titles = [article.Title for article in articles]
        results = self.sentiment_pipeline(titles)
        
        if self.task is NER_TASK:
            for entity in results:
                print(entity)
    
        if self.task is TEXT_TASK:
            for title, sentiment in zip(titles, results):
                index = next(i for i, a in enumerate(articles) if a.Title == title)
                articles[index].Sentiment = (sentiment['label'], sentiment['score'])
                print(f"'{title}' --> {sentiment['label']} ({sentiment['score']:.2f})")
            
        return articles
    

def fetch_hist_ticker(ticker: str):
    ticker = 'TSLA'
    df = yf.download(ticker, period="6mo", interval="1d")

    # Append mock sentiment scores (in production, you'd batch-process sentiment)
    df['Sentiment'] = [0.98 if i % 2 == 0 else 0.3 for i in range(len(df))]

    print(df.tail())

# Main execution
if __name__ == "__main__":
    feeds = {
        "Yahoo Finance": "https://finance.yahoo.com/news/rssindex/", # Start with just Yahoo Finance as a start
    }
    
    sent = ModelAnalysis("dbmdz/bert-large-cased-finetuned-conll03-english", NER_TASK)

    for source, url in feeds.items():
        articles = ingest_rss_feed(url, source)
        sent.run(articles)
        