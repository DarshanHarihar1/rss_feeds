import feedparser
import csv
from db_helper import insert_news_article 
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from collections import defaultdict

# Download NLTK resources (if not already downloaded)
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# Define categories
categories = {
    'terrorism': ['terrorism', 'protest', 'political unrest', 'riot', 'conflict', 'demonstration', 'insurgency', 'uprising', 'civil unrest', 'revolt', 'violence', 'agitation', 'rebellion', 'anarchy', 'coup'],
    'positive': ['positive', 'uplifting', 'inspired', 'win', 'lead', 'victory', 'achievement', 'success', 'happiness', 'joy', 'triumph', 'encouragement', 'empowerment', 'optimism', 'motivation'],
    'natural_disasters': ['natural disasters', 'floods', 'crash', 'flood', 'collapsed', 'died', 'alarm', 'earthquake', 'tsunami', 'hurricane', 'tornado', 'cyclone', 'wildfire', 'drought', 'landslide']
}

def parse_rss(feed_url):
    feed = feedparser.parse(feed_url)
    articles = []
    for entry in feed.entries:
        article = {
            'title': entry.get('title', ''),
            'content': entry.get('summary', ''),
            'pub_date': entry.get('published', ''),
            'source_url': entry.get('link', ''),
        }
        articles.append(article)
    return articles

def get_article_category(title):
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words("english"))
    tokenized_content = word_tokenize(title.lower())
    filtered_content = [word for word in tokenized_content if word not in stop_words]
    lemmatized_content = [lemmatizer.lemmatize(word) for word in filtered_content]

    # Categorize based on keywords
    category_scores = defaultdict(int)
    for word in lemmatized_content:
        for category, keywords in categories.items():
            if any(keyword in word for keyword in keywords):
                category_scores[category] += 1

    # Determine the category with the highest score
    if category_scores:
        max_category = max(category_scores, key=category_scores.get)
        return max_category
    else:
        return 'Others'

rss_feeds = [
    "http://rss.cnn.com/rss/cnn_topstories.rss",
    "http://qz.com/feed",
    "http://feeds.foxnews.com/foxnews/politics",
    "http://feeds.reuters.com/reuters/businessNews",
    "http://feeds.feedburner.com/NewshourWorld",
    "https://feeds.bbci.co.uk/news/world/asia/india/rss.xml",
]

all_articles = []
existing_urls = set()  # Keep track of existing URLs to check for duplicates

for feed_url in rss_feeds:
    articles = parse_rss(feed_url)
    for article in articles:
        # Check if the URL already exists in the set
        if article['source_url'] not in existing_urls:
            # If it's a new article, add it to the list and set
            article['category'] = get_article_category(article['title'])  # Assign category
            all_articles.append(article)
            existing_urls.add(article['source_url'])
            
def save_to_csv(articles, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['title', 'content', 'pub_date', 'source_url', 'category']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for article in articles:
            writer.writerow(article)

save_to_csv(all_articles, 'news_articles.csv')

for article in all_articles:
    insert_news_article(article['title'], article['content'], article['pub_date'], article['source_url'], article['category'])
