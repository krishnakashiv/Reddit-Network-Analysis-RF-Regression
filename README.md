# Reddit-Network-Analysis

The python applications:

reddit_network_sentiment_to_predict_cryptocurrency_price_movement_bitcoin.py
reddit_network_sentiment_to_predict_cryptocurrency_price_movement_etheruem.py

can be run to get all top posts in the subreddits bitcoin and ethereum. The final dataframe is saved as a CSV.

The python application 

reddit_network_graph.py

creates the directed weighted graph of author-author relationship.The normalized page rank of the authors is stored in a CSV.

The Python application

linear_regression_random_forest.py

builds linear regression and random forest to predict the cryptocurrency price points.

Running applications in background:
Example-
CMD : nohup python3 -u reddit_network_sentiment_to_predict_cryptocurrency_price_movement_bitcoin.py &> nohupbitcoin.out &


GITHUB LINK: 
https://github.com/krishnakashiv/Reddit-Network-Analysis-
