"""Consume status objects from the Streaming API and pass them to Redis."""


import json

import redis
import tweepy


with open('Parameters.json') as f:
    p = json.load(f)

r = redis.StrictRedis()


# Add to the tweepy.models.Status class an instance variable containing
# the raw tweet JSON, including Unicode characters.
@classmethod
def parse(cls, api, raw):
    status = cls.first_parse(api, raw)
    status.json = json.dumps(raw, ensure_ascii=False)
    return status

tweepy.models.Status.first_parse = tweepy.models.Status.parse
tweepy.models.Status.parse = parse


class Listener(tweepy.StreamListener):
    
    def on_status(self, data):
        r.lpush('1:2', str(data.json.encode('UTF-8')))
    
    def on_error(self, status_code):
        return True  # Keep the stream alive.


def main():
    auth = tweepy.OAuthHandler(p['consumer_key'], p['consumer_secret'])
    auth.set_access_token(p['access_token'], p['access_token_secret'])
    stream = tweepy.Stream(auth, Listener(), timeout=None)
    stream.filter(p['follow'], p['track'])


if __name__ == '__main__':
    main()


