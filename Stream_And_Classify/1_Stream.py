"""
"""


import codecs
import json
import locale
import sys

import tweepy


# Import Twitter Streaming API OAuth keys and track/follow parameters.
with open('/home/rosspetchler/GSoC/Parameters.json') as f:
    par = json.loads(f.read())


# Wrap sys.stdout into a StreamWriter to allow writing Unicode.
sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)


# Add to the tweepy.models.Status class an instance variable containing
# the raw tweet JSON, including Unicode characters.
@classmethod
def parse(cls, api, raw):
    status = cls.first_parse(api, raw)
    setattr(status, 'json', json.dumps(raw, ensure_ascii=False))
    return status

tweepy.models.Status.first_parse = tweepy.models.Status.parse
tweepy.models.Status.parse = parse


class Listener(tweepy.StreamListener):
    
    def on_status(self, data):
        print data.json
    
    def on_error(self, status_code):
        return True  # Keep the stream alive.


def main():
    auth = tweepy.OAuthHandler(par['twitter_consumer_key'],
                               par['twitter_consumer_secret'])
    auth.set_access_token(par['twitter_access_token'],
                          par['twitter_access_token_secret'])
    
    stream = tweepy.Stream(auth, Listener(), timeout=None)
    stream.filter(par['follow'], par['track'])


if __name__ == '__main__':
    
    main()


