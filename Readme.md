DEPENDENCIES:
1. re - regex module
2. tweepy -  twitter api's
> pip install tweepy
3. textblob - sentiment analysis and word tags
> pip install textblob
> python -m textblob.download_corpora
4. numpy - statistics
> pip install numpy
5. collections - Counter
6. os, requests, json - for genderize.io's API
7. tabulate - pretty print tables
> pip install tabulate
8. datetime - query time evaluation
9. nltk.corpus.stopwords - stop word detection

USAGE:
> python test.py

OUTPUTS:
1. Sentiment breakdown of the query
2. Top 10 words (excluding stop words)
3. Top 10 hash tags
4. Gender breakdown of users
5. Gender wise sentiment breakdown

ADDITIONAL COMMANDS:
> python create_name_dict.py  (creates the offline name dictionary)

REFERENCES:
https://www.geeksforgeeks.org/twitter-sentiment-analysis-using-python/
