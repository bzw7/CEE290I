import re 
import tweepy 
from tweepy import OAuthHandler 
from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer
import numpy as np
from collections import Counter
import os
import requests, json
from tabulate import tabulate
from keys import consumer_key,consumer_secret,access_token,access_token_secret
import datetime
from nltk.corpus import stopwords

data_dir= 'data'
name_file= 'name.npy'

stop = stopwords.words('english')
stop= stop + [re.sub(r'[^A-Za-z0-9]+', '', x) for x in stop]

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
        f_t=[]
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
                # saving gender of user
                parsed_tweet['gender'] = get_gender(clean_word(tweet.user.name.split(' ')[0])) 
                # appending parsed tweet to tweets list 
                if tweet.retweet_count > 0:
                    # if tweet has retweets, ensure that it is appended only once 
                    if parsed_tweet not in tweets: 
                        tweets.append(parsed_tweet)
                        f_t.append(tweet) 
                else: 
                    tweets.append(parsed_tweet)
                    f_t.append(tweet)
            # return parsed tweets 
            return tweets,f_t
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

def get_gender(name):
    name=name.lower()
    try:
        nf=np.load(data_dir+'/'+name_file)
        nf=nf[()]
    except:
        nf={}
    if name in nf:
        return nf[name]
    else:
        try:
            url="name[0]="+name    
            req = requests.get("https://api.genderize.io?" + url)
            results = json.loads(req.text)
            retrn = []
            for result in results:
                if result["gender"] is not None:
                    retrn.append((result["gender"], result["probability"], result["count"]))
                else:
                    retrn.append((u'None',u'0.0',0.0))
        except:
            # print(results["error"])
            return 'None'
        nf[name]=retrn[0][0]
        np.save(data_dir+'/'+name_file,nf)
        return retrn[0][0]

def clean_word(word):
    regex = re.compile('[^a-zA-Z]')
    return regex.sub('', word)

def word_finder(fetched_tweets,num=10):
    ct=[]
    for t in fetched_tweets:
        text=TextBlob(clean_tweet(t.text.lower()).replace('.',''))
        for tt in text.tags:
            if tt[1] not in ["WRB","DT","VBZ","CC","IN","PRP","MD"]:
                cw=clean_word(tt[0])
                if (len(cw)>2) and (cw not in stop):
                    ct.append(cw)
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

    # print(time_finder(fetched_tweets,10))
    if len(tweets)!=0:
        # picking positive tweets from tweets 
        ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive'] 
        # percentage of positive tweets 
        print("\nPositive tweets percentage: {} %".format(100*len(ptweets)/len(tweets))) 
        # picking negative tweets from tweets 
        ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative'] 
        # percentage of negative tweets 
        print("Negative tweets percentage: {} %".format(100*len(ntweets)/len(tweets))) 
        # percentage of neutral tweets 
        print("Neutral tweets percentage: {} %".format(100*(len(tweets)-len(ntweets)-len(ptweets))/len(tweets))) 
        print('\n')
        print(tabulate(word_finder(fetched_tweets,10),headers=['Word','Count'],tablefmt='orgtbl'))
        print('\n')
        print(tabulate(hashtag_finder(fetched_tweets,10),headers=['Hashtag','Count'],tablefmt='orgtbl'))
    else:
        print("ERROR: No Tweets Obtained")

    # picking female names from tweets 
    ftweets = [tweet for tweet in tweets if tweet['gender'] == 'female'] 
    pftweets = [tweet for tweet in ftweets if tweet['sentiment'] == 'positive']
    nftweets = [tweet for tweet in ftweets if tweet['sentiment'] == 'negative']
    
    if len(ftweets)!=0:
        # percentage of female names
        print("\nFemale users percentage: {} %".format(100*len(ftweets)/len(tweets))) 
        print("Female positive reviews percentage: {} %".format(100*len(pftweets)/len(ftweets))) 
        print("Female negative reviews percentage: {} %".format(100*len(nftweets)/len(ftweets))) 
        print("Female neutral reviews percentage: {} %".format(100*(len(ftweets)-len(nftweets)-len(pftweets))/len(ftweets)))
    else:
        print("\nERROR: No female tweets")
    # picking male names from tweets 

    mtweets = [tweet for tweet in tweets if tweet['gender'] == 'male'] 
    pmtweets = [tweet for tweet in mtweets if tweet['sentiment'] == 'positive']
    nmtweets = [tweet for tweet in mtweets if tweet['sentiment'] == 'negative']
    if len(mtweets)!=0:
        # percentage of male names 
        print("\nMale users percentage: {} %".format(100*len(mtweets)/len(tweets))) 
        print("Male positive reviews percentage: {} %".format(100*len(pmtweets)/len(mtweets))) 
        print("Male negative reviews percentage: {} %".format(100*len(nmtweets)/len(mtweets))) 
        print("Male neutral reviews percentage: {} %".format(100*(len(mtweets)-len(nmtweets)-len(pmtweets))/len(mtweets)))
    else:
        print("ERROR: No male tweets")
    
    if len(tweets)!=0:
        print("\nUknonwn names percentage: {} %".format(100*(len(tweets)-len(ftweets)-len(mtweets))/len(tweets)))
    # percentage of unknown names 
    # # printing first 5 positive tweets 
    # print("\n\nPositive tweets:") 
    # for tweet in ptweets[:10]: 
    #      print(tweet['text']) 
  
    # # printing first 5 negative tweets 
    # print("\n\nNegative tweets:") 
    # for tweet in ntweets[:10]: 
    #      print(tweet['text']) 
  
if __name__ == "__main__":
    query=input("Enter Query:\n")
    # query='brunch'
    t1=datetime.datetime.now()
    main(data_dir,query)
    t2=datetime.datetime.now()
    print("\nQuery Time: " + str((t2-t1).seconds) + 's\n')