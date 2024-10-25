from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col, lit
from pyspark.sql.types import StringType, FloatType
import praw
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import re
import emoji
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Spark and NLP Model Initialization
spark = SparkSession.builder.appName("RedditSentimentCryptoDAG").getOrCreate()
tokenizer = AutoTokenizer.from_pretrained("mwkby/distilbert-base-uncased-sentiment-reddit-crypto")
specific_model = pipeline(model="mwkby/distilbert-base-uncased-sentiment-reddit-crypto")

# Reddit API credentials - load from environment variables in a secure setup
client_id = "X"
client_secret = "X"
user_agent = "Research"

default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
    'retries': 1,
}

dag = DAG(
    'reddit_crypto_sentiment_dag',
    default_args=default_args,
    description='Reddit Network Sentiment Analysis to predict Cryptocurrency Price Movement',
    schedule_interval='@daily',
)

# Task 1: Fetch Reddit data using PySpark
def fetch_reddit_data():
    reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent=user_agent)
    hot_posts = reddit.subreddit("bitcoin").top(limit=10000)
    data = [(post.title, post.score, post.id, post.subreddit, post.url, post.num_comments, post.selftext, post.created) for post in hot_posts]
    
    # Convert to Spark DataFrame
    posts_df = spark.createDataFrame(data, schema=['title', 'score', 'id', 'subreddit', 'url', 'num_comments', 'body', 'created'])
    posts_df = posts_df.withColumn("created", col("created").cast("timestamp"))
    posts_df = posts_df.orderBy("created")
    posts_df.write.mode("overwrite").parquet("/path/to/intermediate/reddit_posts.parquet")  # Save as parquet for easy reloading

fetch_data = PythonOperator(
    task_id='fetch_reddit_data',
    python_callable=fetch_reddit_data,
    dag=dag,
)

# Task 2: Sentiment Analysis with PySpark
def analyze_sentiment():
    # Load the data from the intermediate parquet file
    posts_df = spark.read.parquet("/path/to/intermediate/reddit_posts.parquet")

    # Define PySpark UDFs for sentiment analysis
    @udf(StringType())
    def get_sentiment(text):
        return specific_model(text[:450])[0]['label'] if len(text) < 450 else "neutral"  # Simplified for demo purposes

    @udf(FloatType())
    def get_sentiment_score(text):
        sentiment = specific_model(text[:450])[0] if len(text) < 450 else None
        if sentiment:
            return sentiment['score'] if sentiment['label'] == 'positive' else -sentiment['score']
        return 0.0  # Neutral score for missing data

    # Add columns with title and body sentiment scores
    posts_df = posts_df.withColumn("title_sentiment", get_sentiment(col("title")))
    posts_df = posts_df.withColumn("title_score", get_sentiment_score(col("title")))
    posts_df = posts_df.withColumn("body_sentiment", get_sentiment(col("body")))
    posts_df = posts_df.withColumn("body_score", get_sentiment_score(col("body")))

    # Save results back to parquet
    posts_df.write.mode("overwrite").parquet("/path/to/output/reddit_sentiment_analysis.parquet")

analyze_data = PythonOperator(
    task_id='analyze_sentiment',
    python_callable=analyze_sentiment,
    dag=dag,
)

# Task 3: Save the final result to CSV
def save_to_csv():
    # Load the processed data and save it as a CSV
    sentiment_df = spark.read.parquet("/path/to/output/reddit_sentiment_analysis.parquet")
    sentiment_df.toPandas().to_csv('/path/to/output/bitcoin_subreddit_analysis.csv', index=False)

save_data = PythonOperator(
    task_id='save_to_csv',
    python_callable=save_to_csv,
    dag=dag,
)

# Set task dependencies
fetch_data >> analyze_data >> save_data
