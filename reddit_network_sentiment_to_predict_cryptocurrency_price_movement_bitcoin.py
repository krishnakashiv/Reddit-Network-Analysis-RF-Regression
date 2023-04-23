# -*- coding: utf-8 -*-
"""Reddit Network Sentiment to predict Cryptocurrency Price Movement

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1NKnlCpk3yW_C-5_gkzQ6O5Bbx1mIMLyv
"""

#Standard Libraries
import praw
import pandas as pd
import datetime
import warnings
warnings.filterwarnings("always")

#NLP Libraries
import emoji
from nltk.tokenize import RegexpTokenizer
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
nltk.download('stopwords')
nltk.download('punkt')
import re

#Sentiment Analysis Models
from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForSequenceClassification


#PRAW application ID and Secret
reddit = praw.Reddit(
    client_id="DDScYrlvPYFopqlOS3IReQ",
    client_secret="kOzq249feXHiuh3Y4moM8aC1sVaKHA",
    user_agent="Research",
)
reddit.read_only = True

#Get top posts from the subreddit
hot_posts=reddit.subreddit("bitcoin").top(limit=10000)

posts = [] # Empty list

# Cycle through all of the top level posts the generator can provide
for post in hot_posts:
    posts.append([post.title, post.score, post.id, post.subreddit, post.url, post.num_comments, post.selftext, post.created])

# Add the data to a dataframe
posts = pd.DataFrame(posts, columns=['title', 'score', 'id', 'subreddit', 'url', 'num_comments', 'body', 'created'])

posts

#Convert Timestamp to Datetime 
posts['created'] = posts['created'].astype(int)
posts["created"] = posts["created"].apply(lambda x: datetime.datetime.utcfromtimestamp(x).strftime('%d-%m-%Y %H:%M:%S'))

posts["created"] = pd.to_datetime(posts["created"])
print(posts.dtypes)

#Sort posts according to date created
posts.sort_values(by='created', inplace=True)

#Add new columns 
posts["pos_comments"]=0
posts["neg_comments"]=0
posts["avg_comment_score"]=0
posts['avg_comment_score'] = posts['avg_comment_score'].astype(float)
posts['title_score']=0
posts['title_score'] = posts['title_score'].astype(float)
posts['body_score']=0
posts['body_score'] = posts['body_score'].astype(float)
posts

#Import BERT based model from HuggingFace
tokenizer = AutoTokenizer.from_pretrained("mwkby/distilbert-base-uncased-sentiment-reddit-crypto")
specific_model = pipeline(model="mwkby/distilbert-base-uncased-sentiment-reddit-crypto")

"""Do we want to do Sarcasm Detector for all comments and titles?
https://huggingface.co/helinivan/english-sarcasm-detector?text=CIA+Realizes+It%27s+Been+Using+Black+Highlighters+All+These+Years.
"""

##Drawback of reddit data = people write big comments
#Sliding Window Protocol For BERT Limitation

def sliding_window(string, window_size):
    # Split the string into a list of words
    words = string.split()
    
    # Calculate the total number of windows that can be created
    num_windows_divide = len(words)/window_size + 1

    # Create a list to store the windows
    windows = []
    labels = [None]*int(num_windows_divide)
    scores= [None]*int(num_windows_divide)
    # Iterate over the words in the string and extract windows of size `window_size`
    for i in range(0,int(num_windows_divide)):
        k=i*window_size
        window = ' '.join(words[k:k+window_size])
        sentiment_analysis=specific_model(window)
        labels[i]=sentiment_analysis[0]['label']
        if(labels[i]=='postive'):
            scores[i]= sentiment_analysis[0]['score']
        else:
            scores[i]= 0-sentiment_analysis[0]['score']
        windows.append(window)
    
    occurrence = {item: labels.count(item) for item in labels}

    
    negatives = occurrence.get('negative')
    if negatives is None:
        negatives=0

    positives = occurrence.get('positive')
    if positives is None:
        positives=0
    
    score = sum(scores)/len(scores)
    if(positives>negatives):
        sentiment_analysis =[{'label': 'positive', 'score': score}]
        return sentiment_analysis
    elif(negatives>positives):
        sentiment_analysis =[{'label': 'negative', 'score': score}]
        return sentiment_analysis
    elif(negatives==positives):
        if(score>0):
            sentiment_analysis =[{'label': 'positive', 'score': score}]
            return sentiment_analysis
        else:
            sentiment_analysis =[{'label': 'negative', 'score': score}]
            return sentiment_analysis

check_for_async=False

# define a function to process sentiment analysis for a single post
def process_post_sentiment(i, post_id):
    post = reddit.submission(id=post_id)
    post.comments.replace_more(limit=None)
    count = 0
    comment_scores = []
    Comments = []
    for comment in post.comments.list():
        Comments.append(comment.body)

    title_tokens = word_tokenize(posts.at[i,"title"])
    title_tokens_without_sw = [word for word in title_tokens if not word in stopwords.words()]
    filtered_title = (" ").join(title_tokens_without_sw)
    if len(filtered_title) < 450:
        title_sentiment_analysis = specific_model(filtered_title)
    else:
        title_sentiment_analysis = sliding_window(filtered_title, 100)

    body_tokens = word_tokenize(posts.at[i,"body"])
    body_tokens_without_sw = [word for word in body_tokens if not word in stopwords.words()]
    filtered_body = (" ").join(body_tokens_without_sw)
    filtered_body = re.sub('http[s]?://\S+', '', filtered_body)
    if len(filtered_body) < 450:
        body_sentiment_analysis = specific_model(filtered_body)
    else:
        body_sentiment_analysis = sliding_window(filtered_body, 60)

    
    posts.at[i,'pos_comments'] = 0
    posts.at[i,'neg_comments'] = 0
    k = 0
    for comment in Comments:
        comment = re.sub('http[s]?://\S+', '', comment)
        comment_tokens = word_tokenize(comment)
        comment_tokens_without_sw = [word for word in comment_tokens if not word in stopwords.words()]
        
        
        count=count+1
        filtered_comment = re.sub(r'^https?:\/\/.*[\r\n]*', '', (" ").join(comment_tokens_without_sw), flags=re.MULTILINE)
        filtered_comment = re.sub(r"[^a-zA-Z0-9 ]", "", filtered_comment)
        filtered_comment = emoji.replace_emoji(filtered_comment, replace='')
        
        # print("\nID="+submission_id +" --"+str(len(comment_tokens_without_sw))+" "+str(count)+" "+filtered_comment + "\n Actual Comment: ]\n"+comment)
        if(len(comment_tokens_without_sw)<300):
            sentiment_analysis=specific_model(filtered_comment)
        else: #Limitation of BERT
            sentiment_analysis=sliding_window(filtered_comment,75)
            
        if sentiment_analysis[0]['label'] == 'positive':
            comment_scores.append(sentiment_analysis[0]['score'])
            # print("Postive=" +str(posts1.at[i,'pos_comments']))
            posts.at[i,'pos_comments'] = posts.at[i,'pos_comments'] + 1
            k=k+1

        elif sentiment_analysis[0]['label'] == 'negative':
            comment_scores.append(0-sentiment_analysis[0]['score'])
            # print("Negative="+str(posts1.at[i,'neg_comments']))
            posts.at[i,'neg_comments'] = posts.at[i,'neg_comments'] + 1
            k=k+1

    total_comments= int(posts.at[i,'pos_comments']) + int(posts.at[i,'neg_comments'])
    posts.at[i,"avg_comment_score"]= float(sum(comment_scores)/total_comments)
    posts.at[i,"title_score"]= float(title_sentiment_analysis[0]['score']) if title_sentiment_analysis[0]['label']== 'positive'else (0-float(title_sentiment_analysis[0]['score']))
    posts.at[i,"body_score"]= float(body_sentiment_analysis[0]['score']) if body_sentiment_analysis[0]['label']== 'positive'else (0-float(body_sentiment_analysis[0]['score']))
    print(f"{post_id} processed")

count = 0
for i, post_id in posts[['id']].itertuples():
    process_post_sentiment(i, post_id)
    print(str(i)+" - "+post_id+" "+ str(count))
    count=count+1

posts.to_csv('bitcoin_subreddit_analysis.csv')

