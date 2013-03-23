"""Filter Tweets to eliminate non-English, non-located, and retweets."""


import json

import redis


r = redis.StrictRedis()


def filtered(tweet):
    if tweet['user']['lang'] != 'en':
        return True
    
    if tweet['retweeted']:
        return True
    
    location = tweet['user']['location']
    if location == None or location.strip() == '':
        return True
    
    text = tweet['text'].strip().lower().split()
    if any(w in text for w in {'rt', 'retweet', 'via'}):
        return True
    
    return False


def main():
    while True:
        key, data = r.brpop('1:2')
        tweet = json.loads(data)
        if not filtered(tweet):
            r.lpush('2:3', json.dumps(tweet, ensure_ascii=False))


if __name__ == '__main__':
    main()


