import sys
import os
import oauth2 as oauth
import urllib2 as urllib
import json
import re

https_handler = urllib.HTTPSHandler()
signature_method = oauth.SignatureMethod_HMAC_SHA1()

def get_files():
    if len(sys.argv) < 3:
        twitter_deets_file = raw_input("Twitter Details File: ")
        sentiment_file = raw_input("Sentiment File: ")
    else:
        twitter_deets_file = sys.argv[1]
        sentiment_file = sys.argv[2]
        
    def file_exists(filename):
        if os.path.isfile(filename):
            return True
        else:
            print "The file: '%s' does not exist!" % filename
            return False 
                 
    if ((not file_exists(twitter_deets_file)) or (not file_exists(sentiment_file))): sys.exit(0)
           
    return twitter_deets_file, sentiment_file

def file_to_dict(file_location,to_float=False):
    #converts tab deliminated sentiment file to dictionary
    input_file = open(file_location)
    values = {}
    for line in input_file:
        term, score  = line.split("\t")
        if to_float:
            values[term] = float(score)
        else:
            values[term] = re.sub('\\n','',score)
    return values
    
def twitter_request(url, parameters, oauth_consumer, oauth_token):
    #send request to twitter and return response using oauth
    req = oauth.Request.from_consumer_and_token(oauth_consumer,token=oauth_token,
        http_method="GET",http_url=url, parameters=parameters)
    req.sign_request(signature_method, oauth_consumer, oauth_token)

    url = req.to_url()
    
    opener = urllib.OpenerDirector()
    opener.add_handler(https_handler)

    response = opener.open(url)
    return response

def get_twitter_data(input_parameters, oath_consumer, oauth_token, n):
    url = "https://stream.twitter.com/1.1/statuses/filter.json"
    parameters = input_parameters
    response = twitter_request(url, parameters, oath_consumer, oauth_token)
    i = 1
    for line in response:    
        yield line.strip()
        if i == n: return
        i += 1
           
def check_sentiment(tweet_info,scores):
    tweet_text = tweet_info.get('text',None).encode('utf-8').lower()
    if tweet_text is not None:
        all_scores = []
 	for word in tweet_text.split():
            all_scores.append(scores.get(word, 0))
    return sum(all_scores)
    
def user_sentiment(tweet_info):
    print 1
    

if __name__ == '__main__':
    twitter_deets_file, sentiment_file = get_files()
        
    #convert to dictionary
    twitter_deets = file_to_dict(twitter_deets_file)
    
    #set oauth consumer and token
    oauth_consumer = oauth.Consumer(key=twitter_deets['consumer_key'], secret=twitter_deets['consumer_secret'])
    oauth_token    = oauth.Token(key=twitter_deets['access_key'], secret=twitter_deets['access_secret'])
    
    #sentiment scores to dictionary
    scores_dict = file_to_dict(sentiment_file,to_float=True)
    
    #assign parrameters for twitter to filter tweets
    track_parameter = raw_input("Please enter track parameter's (comma seperated list): ")
    n = int(raw_input("Number of tweets to run for: "))
    average_size = int(raw_input("Size of moving average: "))
    
    parameters = [("track",track_parameter)]
    
    moving_average = []
    for i in get_twitter_data(parameters,oauth_consumer,oauth_token,n):
        tweet_info = json.loads(i)
        moving_average.append(check_sentiment(tweet_info,scores_dict))
        print tweet_info.get('text','No tweet information').encode('utf-8').lower()
        print sum(moving_average[-average_size:])/float(len(moving_average[-average_size:]))
    

