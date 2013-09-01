import oauth2 as oauth
import urllib2 as urllib
import json
import re

class twitter_handler:
    def __init__(self,twitter_detials_file):
        self.https_handler = urllib.HTTPSHandler()
        self.signature_method = oauth.SignatureMethod_HMAC_SHA1()        
        self.__details_file_to_oauth(twitter_detials_file)

    def __details_file_to_oauth(self,file_location):
        input_file = open(file_location)
        values = {}
        for line in input_file:
            term, score  = line.split("\t")
            values[term] = re.sub('\\n','',score)
        self.oauth_consumer = oauth.Consumer(key=values['consumer_key'], secret=values['consumer_secret'])
        self.oauth_token    = oauth.Token(key=values['access_key'], secret=values['access_secret'])
     
    def __twitter_request(self,url, parameters, oauth_consumer, oauth_token):
        #send request to twitter and return response using oauth
        req = oauth.Request.from_consumer_and_token(oauth_consumer,token=oauth_token,
            http_method="GET",http_url=url, parameters=parameters)
        req.sign_request(self.signature_method, oauth_consumer, oauth_token)
        url = req.to_url()
        opener = urllib.OpenerDirector()
        opener.add_handler(self.https_handler)
        response = opener.open(url)
        return response
    
    def stream_twitter_data(self,input_parameters,allow_retweets=False):
        url = "https://stream.twitter.com/1.1/statuses/filter.json"
        parameters = input_parameters
        response = self.__twitter_request(url, parameters, self.oauth_consumer, self.oauth_token)
        for line in response:
            tweet = json.loads(line.strip())    
            if ('retweeted_status' not in tweet) or allow_retweets: yield tweet
        
    def get_user_data(self,input_parameters):
        url = "https://api.twitter.com/1.1/statuses/user_timeline.json"
        parameters = input_parameters
        response = self.__twitter_request(url, parameters, self.oauth_consumer, self.oauth_token)
        return json.loads(response.read())


