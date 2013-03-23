"""Match hashtags, usernames, and colloquial names in Tweets to URLs."""


import csv
import json

import redis


r = redis.StrictRedis()


with open('Data/Twitter_Entities.csv') as f:
    next(f)  # Skip header row.
    entities = {value.lower(): url for url, field, value in csv.reader(f)}


def extract_urls(tweet):
    if tweet['entities']['urls']:
        # Tweet contains explicit URL.
        urls = [i['expanded_url'] for i in tweet['entities']['urls']]
    else:
        # Attempt named entity recognition.
        text = tweet['text'].strip().lower().split()
        urls = [entities[token] for token in text if token in entities]
    tweet['url'] = urls[0] if len(set(urls)) == 1 else None
    return tweet


def main():
    while True:
        key, data = r.brpop('2:3')
        tweet = json.loads(data)
        tweet = extract_urls(tweet)
        if tweet['url']:
            r.lpush('3:4', json.dumps(tweet, ensure_ascii=False))


if __name__ == '__main__':
    main()


