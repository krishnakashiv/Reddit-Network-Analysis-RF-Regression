from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
import networkx as nx
import pandas as pd
import praw
from pyspark.sql import SparkSession
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import MinMaxScaler
import datetime

# Set up the Spark session
spark = SparkSession.builder.appName("RedditNetworkGraph").getOrCreate()

# Initialize Reddit API (PRAW)
def initialize_reddit_instance():
    return praw.Reddit(
        client_id="DDScYrlvPYFopqlOS3IReQ",
        client_secret="kOzq249feXHiuh3Y4moM8aC1sVaKHA",
        user_agent="Research", check_for_async=False
    )

# Fetch posts from a subreddit
def fetch_subreddit_posts(subreddit_name, limit=1000):
    reddit = initialize_reddit_instance()
    subreddit = reddit.subreddit(subreddit_name)
    posts = []
    for post in subreddit.top(limit=limit):
        posts.append({
            'title': post.title,
            'score': post.score,
            'id': post.id,
            'subreddit': post.subreddit.display_name,
            'url': post.url,
            'num_comments': post.num_comments,
            'body': post.selftext,
            'created': datetime.datetime.fromtimestamp(post.created)
        })
    return pd.DataFrame(posts)

# DAG task: Combine posts from different subreddits
def load_data():
    bitcoin_df = fetch_subreddit_posts('bitcoin')
    ethereum_df = fetch_subreddit_posts('ethereum')
    combined_df = pd.concat([bitcoin_df, ethereum_df], ignore_index=True)
    return spark.createDataFrame(combined_df)

# DAG task: Build network graph from posts
def build_network_graph(posts_spark_df):
    posts = posts_spark_df.toPandas()  # Convert Spark DataFrame to Pandas for processing
    graph = nx.DiGraph()
    reddit = initialize_reddit_instance()

    for _, row in posts.iterrows():
        submission_id = row['id']
        post = reddit.submission(id=submission_id)
        if post.author:
            author = post.author.name
            graph.add_node(author)
            post.comments.replace_more(limit=None)
            for comment in post.comments:
                if comment.author:
                    commenter = comment.author.name
                    graph.add_node(commenter)
                    if commenter != author:
                        if graph.has_edge(commenter, author):
                            graph[commenter][author]['weight'] += 1
                        else:
                            graph.add_edge(commenter, author, weight=1)
    return graph

# DAG task: Calculate PageRank and save results
def calculate_pagerank_save(graph):
    pagerank = nx.pagerank(graph)
    sorted_pagerank = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)
    df = pd.DataFrame(sorted_pagerank, columns=['author', 'score'])

    # Normalize scores
    ct = ColumnTransformer([('somename', MinMaxScaler(), ['score'])], remainder='passthrough')
    df['score'] = ct.fit_transform(df[['score']])

    # Save to CSV
    df.to_csv('/path/to/save/author_influence.csv', index=False)

# Define Airflow DAG
default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
    'depends_on_past': False,
    'retries': 1,
}
dag = DAG(
    'reddit_network_graph',
    default_args=default_args,
    description='A DAG to analyze Reddit network influence',
    schedule_interval='@daily',
)

# Define tasks
load_data_task = PythonOperator(
    task_id='load_data',
    python_callable=load_data,
    dag=dag,
)

build_graph_task = PythonOperator(
    task_id='build_network_graph',
    python_callable=lambda: build_network_graph(load_data_task.output),
    dag=dag,
)

pagerank_task = PythonOperator(
    task_id='calculate_pagerank_save',
    python_callable=lambda: calculate_pagerank_save(build_graph_task.output),
    dag=dag,
)

# Set task dependencies
load_data_task >> build_graph_task >> pagerank_task
