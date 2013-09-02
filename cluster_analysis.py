import sys
import os
import twitter_tools
import collections

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.cluster import KMeans

def get_file():
    if len(sys.argv) < 3:
        twitter_deets_file = raw_input("Twitter Details File: ")
    else:
        twitter_deets_file = sys.argv[1]
    if os.path.isfile(twitter_deets_file):
        return twitter_deets_file
    else:
        print "The file: '%s' does not exist!" % twitter_deets_file
        sys.exit(0)   
        
def gather_tweets(search_parameters,n_tweets):
    twitter_details_file = get_file()
    twitter_access = twitter_tools.twitter_handler(twitter_details_file)
    
    tweets = [] 
    print "Gathering tweets...\n"
    x = 1
    for tweet_info in twitter_access.stream_twitter_data(search_parameters):
        tweets.append(tweet_info)
        if x % 10 == 0: print str(x) + " of " + str(n_tweets)
        if x == n_tweets: break
        x +=1
    return tweets
    
def cluster_tweets(tweets,clusters):
    print "Clustering tweets..."
    vectorizer = CountVectorizer(ngram_range=(1,10),min_df = 2)
    tweet_word_matrix = vectorizer.fit_transform([i['text'] for i in tweets])
    clf = KMeans(n_clusters=clusters)
    return vectorizer.inverse_transform(tweet_word_matrix), clf.fit_predict(tweet_word_matrix)
    
if __name__ == "__main__":
    track_parameter = raw_input("Enter search terms: ")
    search_parameters = [("track",track_parameter)]
    while True:
        n_tweets = raw_input("Number of tweets to scan: ")
        try:
            n_tweets = int(n_tweets)
            break
        except:
            print "Number of tweets must be an integer!\n"
    
    tweets = gather_tweets(search_parameters,n_tweets)
    word_arrays, tweet_categories = cluster_tweets(tweets,10)
    
    """
    for i in range(len(tweets)):
        print "Tweet: " + tweets[i]['text'] 
        print "placed in category: " + str(tweet_categories[i]) + "\n"
    """
    
category_words = collections.defaultdict(list)
for i in range(len(tweet_categories)):
    category_words[tweet_categories[i]].append(word_arrays[i])
#flattens list, counts and counts

count_category_words = {}
set_category_words = {}
removed_duplicates = {}
for i in category_words:
    category_words[i] = [item for sublist in category_words[i] for item in sublist]
    set_category_words[i] = collections.Counter(category_words[i])
    for j in set_category_words:
        if i is not j:
            removed_duplicates[i] = [k for k in category_words[i] if set_category_words[j][k] < 3]

for i in removed_duplicates:
    removed_duplicates[i] = collections.Counter(removed_duplicates[i])
    print removed_duplicates[i].most_common(5)
    

    
    

    
                            

