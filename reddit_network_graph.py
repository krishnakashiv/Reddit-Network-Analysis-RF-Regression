# -*- coding: utf-8 -*-
"""Reddit Network Graph.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1GHjznrYX5XfpxNa8bTznKnjU-oIArc-Z
"""

import networkx as nx
import pandas as pd
import datetime
import praw
import networkx as nx

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import MinMaxScaler

print("Starting execu")

# Initialize the PRAW Reddit instance
reddit = praw.Reddit(
    client_id="DDScYrlvPYFopqlOS3IReQ",
    client_secret="kOzq249feXHiuh3Y4moM8aC1sVaKHA",
    user_agent="Research", check_for_async=False
)

reddit.read_only = True

# Specify the subreddit to analyze BITCOIN
subreddit = reddit.subreddit('bitcoin')

# Retrieve the top posts in the subreddit
top_posts_bitcoin = subreddit.top(limit=1000)

top_posts_bitcoin

posts_bitcoin = [] # Empty list

# Cycle through all of the top level posts the generator can provide
for post in top_posts_bitcoin:
    posts_bitcoin.append([post.title, post.score, post.id, post.subreddit, post.url, post.num_comments, post.selftext, post.created])


# Add the data to a dataframe
posts_bitcoin = pd.DataFrame(posts_bitcoin, columns=['title', 'score', 'id', 'subreddit', 'url', 'num_comments', 'body', 'created'])

posts_bitcoin

# Specify the subreddit to analyze Eth
subreddit = reddit.subreddit('ethereum')

# Retrieve the top posts in the subreddit
top_posts_ethereum = subreddit.top(limit=1000)

top_posts_ethereum

posts_ethereum = [] # Empty list

# Cycle through all of the top level posts the generator can provide
for post1 in top_posts_ethereum:
    posts_ethereum.append([post1.title, post1.score, post1.id, post1.subreddit, post1.url, post1.num_comments, post1.selftext, post1.created])


# Add the data to a dataframe
posts_ethereum = pd.DataFrame(posts_ethereum, columns=['title', 'score', 'id', 'subreddit', 'url', 'num_comments', 'body', 'created'])

posts_ethereum

posts = pd.concat([posts_ethereum, posts_bitcoin], ignore_index=True)

posts

posts

graph = nx.DiGraph()
count = 0
for i, row in posts.iterrows():
    submission_id=posts.at[i,'id']
    post=reddit.submission(id=submission_id)
    print(count)
    count+=1
    post.comments.replace_more(limit=None)
    if(post.author != None):
        author = post.author.name
        print(author)
        if author not in graph:
            graph.add_node(author)
        for comment in post.comments:
            if(comment.author != None):
                commenter = comment.author.name
                graph.add_node(commenter)
                if commenter != author and commenter in graph:
                    if graph.has_edge(commenter, author):
                        graph[commenter][author]['weight'] += 1
                    else:
                        graph.add_edge(commenter, author, weight=1)

# # Compute the centrality measures for each node in the graph
# degree_centrality = nx.degree_centrality(graph)
# betweenness_centrality = nx.betweenness_centrality(graph)
# eigenvector_centrality = nx.eigenvector_centrality(graph)

# # Sort the authors by their centrality scores and output the top authors
# degree_sorted = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)
# betweenness_sorted = sorted(betweenness_centrality.items(), key=lambda x: x[1], reverse=True)
# eigenvector_sorted = sorted(eigenvector_centrality.items(), key=lambda x: x[1], reverse=True)

# print('Top 10 authors by degree centrality:')
# for author, centrality in degree_sorted[:10]:
#     print(author, centrality)

# print('Top 10 authors by betweenness centrality:')
# for author, centrality in betweenness_sorted[:10]:
#     print(author, centrality)

# print('Top 10 authors by eigenvector centrality:')
# for author, centrality in eigenvector_sorted[:10]:
#     print(author, centrality)

print(graph.number_of_nodes())
print(graph.number_of_nodes())

pagerank = nx.pagerank(graph)

# Print the top 10 authors by PageRank value
sorted_pagerank = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)
for author, score in sorted_pagerank[:10]:
    print(f'{author}: {score}')

df = pd.DataFrame(sorted_pagerank, columns=['author', 'score'])

df.head()

features = df

ct = ColumnTransformer([
        ('somename', MinMaxScaler(), ['score'])
    ], remainder='passthrough')

final_page_rank=ct.fit_transform(features)
type(final_page_rank)

final_df= pd.DataFrame(data=final_page_rank,columns=['author', 'score'])
final_df.to_csv('autor_influnce.csv')
