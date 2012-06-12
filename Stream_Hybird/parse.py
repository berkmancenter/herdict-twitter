"""
Main Docstring

Make parse_user_mentions remove nonprintable characters

Implement logging

"""
import datetime
import HTMLParser
import json
import Queue
import re
import string
import threading

# import cld  # Requires glibc-2.14
import nltk
import placemaker
import pymongo
import redis


# Import parameters.
with open('/home/twitter-data/docs/parameters.json') as f:
    par = json.loads(f.read())


# Intialize the Placemaker class.
p = placemaker.placemaker(par['placemaker_consumer_key'])

# Connect to MongoDB.
conn = pymongo.Connection(par['server_name'])
db = getattr(conn, par['database_name'])

# Connect to Redis.
r = redis.StrictRedis()


def parse_status(tweet):
    
    # Subset tweet dictionary.
    drop = ['entities', 'user', 'id_str',
            'in_reply_to_user_id_str', 'in_reply_to_status_id_str']
    status = dict((k, tweet[k]) for k in tweet if k not in drop)
    
    # If a status is retweeted, then insert that retweeted status into the
    # cache and the replace this status's retweeted_status with the retweeted
    # status's tweet ID.
    if status.has_key('retweeted_status'):
        retweet = {'_id'  : status['retweeted_status']['id'],
                   'json' : status['retweeted_status']}
        try:
            db.cache.insert(retweet, safe=True)
            r.rpush('{}_cached'.format(par['database_name']), retweet['_id'])
        except pymongo.errors.DuplicateKeyError:
            pass
        status['retweeted_status'] = retweet['_id']
    
    # Escape XML character entity encoding.
    status['text'] = HTMLParser.HTMLParser().unescape(status['text'])
    
    # Remove non-printable characters from status text.
    status['text'] = ''.join(l for l in status['text'] if l in string.printable)
    
    # Preprocess text (1/3).
    t = status['text'].lower().split()
    t = [w for w in t if not w.startswith(('#', 'http', '@'))]
    t = nltk.word_tokenize(' '.join(t))
    t = [''.join(l for l in w if l not in string.punctuation) for w in t]
    t = [w for w in t if w not in nltk.corpus.stopwords.words('english')]
    
    # Detect retweets.
    status['detected_retweet'] = any(w in t for w in ['rt', 'retweet', 'via'])
    
    # Preprocess text (2/3)
    t = [w for w in t if len(w) >= 3]
    
    # Detect language. Requires glibc-2.14.
    #try:
    #    detected_lang, reliable = cld.detect(' '.join(t), isPlainText=True)[1:3]
    #	status['detected_lang'] = detected_lang if reliable else None
    #except UnicodeEncodeError:
    #    status['detected_lang'] = None
    
    # Preprocess text (3/3).
    status['preprocessed'] = [nltk.PorterStemmer().stem(w) for w in t]
    
    # Extract source link target and remove non-printable characters.
    source = re.compile(r'<.*?>').sub('', status['source'])
    source = ''.join(l for l in source if l in string.printable)
    status['source'] = source.strip()
    
    # Extract Tweet timestamp and convert to %Y-%m-%d %H:%M:%S.
    status['created_at'] = str(datetime.datetime.strptime(status['created_at'],
                               '%a %b %d %H:%M:%S +0000 %Y'))
    
    # Add Twitter User ID.
    status['user_id'] = tweet['user']['id']
    
    # Rename tweet id as _id.
    status['_id'] = tweet['id']
    del status['id']
    
    return status


def parse_hashtags(hts):
    """Extracts hashtags from the hashtag entity.
    
    Params:
        hts: The value associated with tweet['entities']['hashtags'], which is
            a list of the form:
                [{indices: [63, 72], text: TeaParty},
                 {indices: [73, 78], text: TCOT}]
    """
    # Extract hashtag text and remove non-printable characters.
    hts = [''.join(l for l in h['text'] if l in string.printable) for h in hts]
    # Remove empty strings that the previous step may have created.
    hts = [h for h in hts if h]
    # If the list still contains hashtags, return the list.
    if hts:
        return hts


def parse_user_mentions(ums):
    for um in ums:
        for k in ['screen_name', 'name']:
            um[k] = ''.join(l for l in um[k] if l in string.printable)
        for k in ['id_str', 'indices']:
            del um[k]
    return ums


def parse_user(user):
    
    # Subset tweet dictionary.
    drop = ['id_str', 'following', 'follow_request_sent']
    user = dict((k, user[k]) for k in user if k not in drop)
    
    """
    # Geoparse.
    if user['location']:
        location = user['location'].strip()
        location = ''.join(l for l in location if l in string.printable)
        
        # Extract known coordinates.
        if location[0:2].lower().strip() == 't: ':
            coordinates = location[3:].split(',')
            place = {'_id'       : user['id'],
                     'latitude'  : int(coordinates[0]),
                     'longitude' : int(coordinates[1])}
            db.locations.save(place, safe=True)
        elif location[0:7].lower().strip() == 'iphone: ':
            coordinates = location[8:].split(',')
            place = {'_id'       : user['id'],
                     'latitude'  : int(coordinates[0]),
                     'longitude' : int(coordinates[1])}
            db.locations.save(place, safe=True)
        
        # Else, geoparse location.
        else:
            p.find_places(location)
            if len(p.places) == 1:
                place = {'_id'        : user['id'],
                         'place_name' : p.places[0].name,
                         'place_type' : p.places[0].placetype,
                         'latitude'   : p.places[0].centroid.latitude,
                         'longitude'  : p.places[0].centroid.longitude,
                         'confidence' : p.places[0].confidence}
                db.locations.save(place, safe=True)
    """

    # Extract User timestamp and convert to %Y-%m-%d %H:%M:%S.
    user['created_at'] = str(datetime.datetime.strptime(user['created_at'],
                             '%a %b %d %H:%M:%S +0000 %Y'))

    # Rename favourites_count as favorites_count. Beware the British!
    user['favorites_count'] = user['favourites_count']
    del user['favourites_count']

    # Use User ID as the index in the database collection.
    user['_id'] = user['id']
    del user['id']
    
    return user


class ThreadParse(threading.Thread):
    """
    Write a docstring here
    """
    
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
    
    def run(self):
        while True:
            # Get Tweet ID from queue.
            _id = self.queue.get()
           
            # Parse cached Tweet.
            doc = db.cache.find_one({'_id' : _id})['json']
            if isinstance(doc, (str, unicode)):
                doc = json.loads(doc)
            try:
                # If the Tweet has URLs, pass them to parse_urls.py.
                if doc['entities']['urls']:
                    msg = {'_id' : _id, 'urls' : doc['entities']['urls']}
                    r.rpush('%s_urls' % par['database_name'], msg)
                if doc['entities']['hashtags']:
                    hts = parse_hashtags(doc['entities']['hashtags'])
                    if hts:
                        hts = {'_id' : _id, 'hashtags' : hts}
                        db.hashtags.insert(hts, safe=True)
                if doc['entities']['user_mentions']:
                    ums = parse_user_mentions(doc['entities']['user_mentions'])
                    ums = {'_id' : _id, 'user_mentions' : ums}
                    db.user_mentions.insert(ums, safe=True)
                # Parse status element.
                sts = parse_status(doc)
                db.statuses.insert(sts, safe=True)
                # Parse user element.
                usr = parse_user(doc['user'])
                db.users.save(usr, safe=True)  # Upsert user.
            except pymongo.errors.DuplicateKeyError:
                pass
            except Exception as e:
                print e
                pass
        
        # Signal to the queue that the current job is done.
        self.queue.task_done()


def main():
    
    # Define queue.
    queue = Queue.Queue()
    
    # Spawn a pool of threads, and pass a queue instance to each.
    for i in range(20):
        t = ThreadParse(queue)
        t.setDaemon(True)
        t.start()
    
    while True:
        # This scales across multiple hosts because when they all block for
        # the same key, they are put in a FIFO queue.
        _id = int(r.blpop('{}_cached'.format(par['database_name']))[1])
        queue.put(_id)
    
    # Shut down.
    queue.join()  # Blocks until all items in the queue have been processed.
    conn.disconnect()


if __name__ == '__main__':
    
    main()


