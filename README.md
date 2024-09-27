This project aims to analyze sentiment data from Reddit posts in cryptocurrency subreddits and apply machine learning models to predict price movements for Bitcoin and Ethereum. It also includes network graph analysis to explore relationships between Reddit authors and their influence within the subreddit communities.

Applications Overview
1. Sentiment Analysis for Price Prediction
Files:
reddit_network_sentiment_to_predict_cryptocurrency_price_movement_bitcoin.py
reddit_network_sentiment_to_predict_cryptocurrency_price_movement_etheruem.py
These Python scripts collect Reddit data from the subreddits r/bitcoin and r/ethereum. They fetch all top posts over a given period and analyze their sentiment using Natural Language Processing (NLP) techniques.

After processing the data, the final output is stored in a CSV file. The CSV contains key metrics such as:

Post ID
Post Title
Sentiment Score
Author
Number of Upvotes, Downvotes, Comments
Date and Time of Posting
This data is then used as input for further analysis or model building.

Output:
bitcoin_sentiment_data.csv
ethereum_sentiment_data.csv
Command to run (example):
bash
Copy code
nohup python3 -u reddit_network_sentiment_to_predict_cryptocurrency_price_movement_bitcoin.py &> nohup_bitcoin.out &
This runs the script in the background while saving logs to the nohup_bitcoin.out file.

2. Author-Author Network Graph Creation
File:
reddit_network_graph.py
This script builds a directed weighted graph that represents relationships between Reddit authors in the chosen subreddits. The edges of the graph represent interactions between authors (e.g., replies, comments), and the weights represent the frequency or intensity of these interactions.

The script applies PageRank to identify the most influential authors within the subreddit, and the results are saved in a CSV file.

Key Features:
Directed, weighted graph of Reddit author relationships.
Normalized PageRank values for each author to evaluate their influence in the subreddit.
Output:
author_network_bitcoin.csv
author_network_ethereum.csv
Command to run:
bash
Copy code
python3 reddit_network_graph.py
3. Price Prediction using Machine Learning
File:
linear_regression_random_forest.py
This script uses the sentiment data generated in the previous steps and builds two machine learning models—Linear Regression and Random Forest—to predict future cryptocurrency price points (Bitcoin or Ethereum) based on historical sentiment trends.

Models Built:
Linear Regression: A statistical model that assumes a linear relationship between input features (sentiment scores, post engagement metrics, etc.) and cryptocurrency prices.
Random Forest: An ensemble machine learning model that builds multiple decision trees to capture more complex patterns in the data.
The script applies cross-validation to evaluate model performance and outputs key metrics such as Mean Squared Error (MSE) and R-squared (R²).

Command to run:
python3 linear_regression_random_forest.py

Running Applications in the Background
To run these applications in the background, you can use the nohup command to prevent them from stopping if your terminal session ends.

Example Command:
nohup python3 -u reddit_network_sentiment_to_predict_cryptocurrency_price_movement_bitcoin.py &> nohup_bitcoin.out &

In this example:

nohup ensures the program continues running after the terminal is closed.
-u allows for unbuffered output (ensuring real-time log updates).
&> redirects both standard output and error to the nohup_bitcoin.out file.
& runs the process in the background.


Requirements
Ensure you have the following dependencies installed before running the scripts:

Python 3.x
pandas
networkx
nltk
scikit-learn
requests
matplotlib (for graph visualization)

Data Sources
Reddit API: Used to collect posts from subreddits r/bitcoin and r/ethereum.
Cryptocurrency Prices: Historical price data is fetched from a relevant cryptocurrency API (e.g., CoinGecko).
