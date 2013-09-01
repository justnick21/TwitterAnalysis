import sys
import os
import twitter_tools

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

def file_to_dict(file_location):
    input_file = open(file_location)
    values = {}
    for line in input_file:
        term, score  = line.split("\t")
        values[term] = float(score)
    return values
    
def check_sentiment(tweet_info,scores):
    tweet_text = tweet_info.get('text',None).encode('utf-8').lower()
    if tweet_text is not None:
        all_scores = []
 	for word in tweet_text.split():
            all_scores.append(scores.get(word, 0))
    return sum(all_scores)
    
def get_user_sentiment(tweet_list,scores):
    all_sentiments = []
    for tweet in tweet_list:
        all_sentiments.append(check_sentiment(tweet,scores))
    return sum(all_sentiments)/float(len(all_sentiments))



def main():
    twitter_details_file, sentiment_file = get_files()
    twitter_access = twitter_tools.twitter_handler(twitter_details_file)    
    
    scores_dict = file_to_dict(sentiment_file)
    
    track_parameter = raw_input("Enter search terms: ")
    n_tweets = int(raw_input("Number of tweets to scan: "))
    average_size = int(raw_input("Size of moving average: "))
    
    search_parameters = [("track",track_parameter)]
    moving_average = []
    x = 1
    for tweet_info in twitter_access.stream_twitter_data(search_parameters):
        user_parameters = [('user_id',tweet_info['user']['id']),('count',20),('include_rts','false')]
        user_tweet_list = twitter_access.get_user_data(user_parameters)
        
        #calculate average user sentiment for 'count' number of posts
        user_sentiment = get_user_sentiment(user_tweet_list,scores_dict)
        tweet_sentiment = check_sentiment(tweet_info,scores_dict)
        moving_average.append(tweet_sentiment-user_sentiment)
        
        #print details
        print tweet_info.get('text','No tweet information').encode('utf-8').lower()
        print "User Sentiment: " + str(user_sentiment) + ", Tweet Sentiment: " \
            + str(tweet_sentiment) + ", Adjusted User Sentiment: " + str(tweet_sentiment-user_sentiment) 
        print sum(moving_average[-average_size:])/float(len(moving_average[-average_size:]))
        print "\n"
        
        if x == n_tweets: break
        x += 1       
            
if __name__ == '__main__':
    main()
    


