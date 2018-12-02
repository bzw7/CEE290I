import re 
import tweepy 
from tweepy import OAuthHandler 
from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer
import numpy as np
from collections import Counter
import os
from keys import consumer_key,consumer_secret,access_token,access_token_secret

class TwitterClient(object): 
    ''' 
    Generic Twitter Class for sentiment analysis. 
    '''
    def __init__(self): 
        ''' 
        Class constructor or initialization method. 
        '''
        # attempt authentication 
        try: 
            # create OAuthHandler object 
            self.auth = OAuthHandler(consumer_key, consumer_secret) 
            # set access token and secret 
            self.auth.set_access_token(access_token, access_token_secret) 
            # create tweepy API object to fetch tweets 
            self.api = tweepy.API(self.auth) 
        except: 
            print("Error: Authentication Failed") 
  
    def get_tweets(self, query, count, max_tweets = 1000): 
        ''' 
        Main function to fetch tweets and parse them. 
        '''
        # empty list to store parsed tweets 
        tweets = []
        if count>max_tweets:
            count=max_tweets
        try: 
            # call twitter api to fetch tweets 
            fetched_tweets = [status for status in tweepy.Cursor(self.api.search, q=query).items(count)]
            # parsing tweets one by one 
            for tweet in fetched_tweets: 
                # empty dictionary to store required params of a tweet 
                parsed_tweet = {}  
                # saving text of tweet 
                parsed_tweet['text'] = tweet.text 
                # saving sentiment of tweet 
                parsed_tweet['sentiment'] = get_tweet_sentiment(tweet.text) 
                # appending parsed tweet to tweets list 
                if tweet.retweet_count > 0:
                    # if tweet has retweets, ensure that it is appended only once 
                    if parsed_tweet not in tweets: 
                        tweets.append(parsed_tweet) 
                else: 
                    tweets.append(parsed_tweet) 
            # return parsed tweets 
            return tweets,fetched_tweets
        except tweepy.TweepError as e: 
            # print error (if any) 
            print("Error : " + str(e))

def clean_tweet(tweet): 
    ''' 
    Utility function to clean tweet text by removing links, special characters 
    using simple regex statements. 
    '''
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) |(\w+:\/\/\S+)", " ", tweet).split())

def hashtag_finder(fetched_tweets,num=10):
    ct=[]
    for t in fetched_tweets:
        for ht in t.entities['hashtags']:
            ct.append(ht['text'])
    c=Counter(ct)
    return c.most_common()[:num]

def time_finder(fetched_tweets,num=10):
    ct=[]
    for t in fetched_tweets:
        ct.append(t.created_at.hour)
    c=Counter(ct)
    return c.most_common()[:num]

def word_finder(fetched_tweets,num=10):
    ct=[]
    for t in fetched_tweets:
        # input(clean_tweet(t.text.lower()).split(' '))
        ct=ct+clean_tweet(t.text.lower()).split(' ')
    c=Counter(ct)
    return c.most_common()[:num]

def get_tweet_sentiment(tweet): 
    ''' 
    Utility function to classify sentiment of passed tweet 
    using textblob's sentiment method 
    '''
    # create TextBlob object of passed tweet text 
    analysis = TextBlob(clean_tweet(tweet)) 
    # set sentiment 
    if analysis.sentiment.polarity > 0: 
        return 'positive'
    elif analysis.sentiment.polarity == 0: 
        return 'neutral'
    else: 
        return 'negative'

def main(data_dir,query,count=100,Save=True,load=True):
    # try opening file if exists
    if load:
        try:
            tweets = np.load(data_dir+'/'+query + '_' + str(count) + '.npy')
            fetched_tweets = np.load(data_dir+'/'+query + '_' + str(count) + '_r.npy')
        except:
            load=False
    if not load:
    # creating object of TwitterClient Class 
        api = TwitterClient() 
        # calling function to get tweets 
        tweets,fetched_tweets = api.get_tweets(query = query, count = count)
        if Save:
            np.save(data_dir+'/'+query + '_' + str(count) + '_r.npy', fetched_tweets)
            np.save(data_dir+'/'+query + '_' + str(count) + '.npy', tweets)
    print(len(tweets))
    print(word_finder(fetched_tweets,20))
    print(hashtag_finder(fetched_tweets,10))
    print(time_finder(fetched_tweets,10))
    # picking positive tweets from tweets 
    ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive'] 
    # percentage of positive tweets 
    print("Positive tweets percentage: {} %".format(100*len(ptweets)/len(tweets))) 
    # picking negative tweets from tweets 
    ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative'] 
    # percentage of negative tweets 
    print("Negative tweets percentage: {} %".format(100*len(ntweets)/len(tweets))) 
    # percentage of neutral tweets 
    print("Neutral tweets percentage: {} %".format(100*(len(tweets)-len(ntweets)-len(ptweets))/len(tweets))) 
  
    # printing first 5 positive tweets 
    print("\n\nPositive tweets:") 
    for tweet in ptweets[:10]: 
         print(tweet['text']) 
  
    # printing first 5 negative tweets 
    print("\n\nNegative tweets:") 
    for tweet in ntweets[:10]: 
         print(tweet['text']) 
  
if __name__ == "__main__":
    data_dir= 'data'
    query=input("Enter Query:\n")
    main(data_dir,query)