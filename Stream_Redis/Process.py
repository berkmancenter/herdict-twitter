"""
TODO: Implement logging
"""


import datetime
import HTMLParser
import json
import Queue
import re
import string
import threading
import urllib
import urlparse

# import cld  # Requires glibc-2.14
import nltk
import placemaker
import pymongo
import redis


# Import parameters.
with open('/home/twitter-data/docs/parameters.json') as f:
    par = json.loads(f.read())


# Connect to Redis.
r = redis.StrictRedis()


# Intialize the Placemaker class.
p = placemaker.placemaker(par['placemaker_consumer_key'])


'''
...
t = [w for w in t if w not in nltk.corpus.stopwords.words('english')]

# Detect retweets.
status['detected_retweet'] = any(w in t for w in ['rt', 'retweet', 'via'])

t = [w for w in t if len(w) >= 3]

#try:
#    detected_lang, reliable = cld.detect(' '.join(t), isPlainText=True)[1:3]
#	status['detected_lang'] = detected_lang if reliable else None
#except UnicodeEncodeError:
#    status['detected_lang'] = None

status['preprocessed'] = [nltk.PorterStemmer().stem(w) for w in t]
'''


def subset_dictionary(dictionary, keys_to_keep):
    return dict((k, dictionary[k]) for k in dictionary if k in keys_to_keep)


def convert_datetime(string):
    date = datetime.datetime.strptime(string, '%a %b %d %H:%M:%S +0000 %Y')
    return date.isoformat()


def preprocess(tweet):
    text = tweet['text'].lower().split()
    #text = [w for w in text if not w.startswith(['#', 'http', '@'])]
    text = [w for w in text if not w.startswith('http')]
    text = nltk.word_tokenize(' '.join(text))
    text = [''.join(l for l in w if l not in string.punctuation) for w in text]
    text = [w for w in text if w not in nltk.corpus.stopwords.words('english')]
    text = [w for w in text if len(w) >= 3]
    text = [nltk.PorterStemmer().stem(w) for w in text]
    return text


def geolocate(tweet):
    location = tweet['user']['location']
    if location == None:
        return
    location = location.lower().strip()
    if location == '':
        return
    
    # Extract known coordinates.
    if location[1:4] == 't: ':
        coordinates = location[5:].split(',')
        return (int(coordinates[1]), int(coordinates[0]))
    if location[0:7] == 'iphone: ':
        coordinates = location[8:].split(',')
        return (int(coordinates[1]), int(coordinates[0]))
    
    # If location rather than coordinates, try geoparsing.
    p.find_places(location)
    if (len(p.places) == 1 and p.places[0].confidence >= 6 and
        p.places[0].placetype not in ['Country', 'Continent']):
        return (p.places[0].centroid.longitude, p.places[0].centroid.latitude)


def unshorten(url):
    """Unshortens a URL, if possible.
    
    Sends a header request for a given URL, and returns the target location
    (if the URL is redirected) or the URL (if it is not redirected).
    
    Args:
        url: A string URL, including the scheme (usually http).
    
    Returns:
        If the URL is redirected, the target URL.
        If the URL is not redirected, the URL.
        In the case of an error, the URL.
    """
    try:
        parsed = urlparse.urlparse(url)
        h = httplib.HTTPConnection(parsed.netloc)
        h.request('HEAD', parsed.path)
        response = h.getresponse()
        if response.status / 100 == 3 and response.getheader('Location'):
            return response.getheader('Location')
        else:
            return url
    except httplib.HTTPException as e:
        return url


def process(tweet):
    # Process status object.
    if tweet.has_key('retweeted_status'):
        r.rpush('cached', str(status['retweeted_status']))
    keys_to_keep = ['coordinates', 'created_at', 'entities', 'geo',
                    'in_reply_to_screen_name', 'in_reply_to_status_id',
                    'in_reply_to_user_id', 'retweeted', 'retweeted_status',
                    'source', 'text', 'user']
    tweet = subset_dictionary(tweet, keys_to_keep)
    tweet['created_at'] = convert_datetime(tweet['created_at'])
    tweet['text'] = HTMLParser.HTMLParser().unescape(tweet['text'])
    tweet['source'] = re.compile(r'<.*?>').sub('', tweet['source']).strip()
    #
    # Process user object.
    keys_to_keep = ['created_at', 'description', 'followers_count', 'id',
                    'lang', 'location', 'name', 'screen_name',
                    'statuses_count']
    tweet['user'] = subset_dictionary(tweet['user'], keys_to_keep)
    tweet['user']['created_at'] = convert_datetime(tweet['user']['created_at'])
    #tweet['user']['location'] = geolocate(tweet['user']['location'])
    #
    # Process entities.
    tweet['entities']['hashtags'] = [
        h['text'].lower() for h in tweet['entities']['hashtags']]
    tweet['entities']['user_mentions'] = [
        subset_dictionary(u, ['id', 'name', 'screen_name'])
    tweet['entities']['urls'] = [
        unshorten(u['expanded_url']) for u in tweet['entities']['urls']]
    #
    return tweet


class ThreadParse(threading.Thread):
    """
    Write a docstring here
    """
    
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
    
    def run(self):
        while True:
            tweet = self.queue.get()
            tweet = json.loads(tweet)
            try:
                tweet = process(tweet)
            except Exception as e:
                print e
                pass
        
        # Signal to the queue that the current job is done.
        self.queue.task_done()


def main():
    
    # Spawn a pool of threads and pass a queue instance to each.
    queue = Queue.Queue()
    for number_of_worker_threads in range(10):
        t = ThreadParse(queue)
        t.setDaemon(True)
        t.start()
    
    # Maintain a blocking listen on the Redis key containing cached Tweets.
    # Pop off each cached Tweet and add it to the queue.
    while True:
        queue.put(r.blpop('cached'))
    
    queue.join()  # Blocks until all items in the queue have been processed.


if __name__ == '__main__':
    
    main()


