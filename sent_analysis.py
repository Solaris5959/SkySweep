from transformers import pipeline
# Load FinBERT sentiment model
sentiment_pipeline = pipeline("text-classification", model="yiyanghkust/finbert-tone")

# Example news headline
news_headline = "Tesla reports record-breaking revenue for Q4."

# Analyze sentiment
result = sentiment_pipeline(news_headline)
print(result)
