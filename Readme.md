DEPENDENCIES:
re - regex module
tweepy -  twitter api's
textblob - sentiment analysis and word tags
numpy - statistics
collections - Counter
os, requests, json - for genderize.io's API
tabulate - pretty print tables
datetime - query time evaluation
nltk.corpus.stopwords - stop word detection

USAGE:
>> python test.py

OUTPUTS:
1. Sentiment breakdown of the query
2. Top 10 words (excluding stop words)
3. Top 10 hash tags
4. Gender breakdown of users
5. Gender wise sentiment breakdown

ADDITIONAL COMMANDS:
>> python create_name_dict.py  (creates the offline name dictionary)

REFERENCES:
https://www.geeksforgeeks.org/twitter-sentiment-analysis-using-python/
