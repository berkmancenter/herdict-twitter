# -*- coding: utf-8 -*-


"""
"""


import codecs
import json
import locale
import sys

import placemaker


# Import Twitter Streaming API OAuth keys and track/follow parameters.
with open('/home/rosspetchler/GSoC/Parameters.json') as f:
    par = json.loads(f.read())


# Wrap sys.stdout into a StreamWriter to allow writing Unicode.
sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)


# Initialize Placemaker class and connect to Yahoo! Placemaker API.
p = placemaker.placemaker(par['placemaker_consumer_key'])


def related(tweet):
    
    if tweet['user']['lang'] != 'en':
        return False
    
    if tweet['retweeted']:
        return False
    
    if tweet['entities']['urls']:
        return False
    
    location = tweet['user']['location']
    if location == None or location.strip() == '':
        return False
    
    text = tweet['text'].strip().lower().split()
    if any(w in text for w in ['rt', 'retweet', 'via']):
        return False
    
    return True


def geoparse(tweet):
    
    location = tweet['user']['location']
    
    if location[0:3] == 'ÜT: ':
        coordinates = location[4:].split(',')
        return [int(coordinates[1]), int(coordinates[0])]
    
    if location[0:7] == 'iPhone: ':
        coordinates = location[8:].split(',')
        return [int(coordinates[1]), int(coordinates[0])]
    
    else:
        p.find_places(location)
        
        if len(p.places) != 1:
            return
        
        if p.places[0].confidence < 6:
            return
        
        if p.places[0].placetype in ['Continent', 'Country']:
            return
        
        centroid = p.places[0].centroid
        if not (  25.15858 <= centroid.latitude  <=  49.37177 and 
                -124.63551 <= centroid.longitude <= -67.04179):
            return  # Not in lower 48 United States.
        
        return [centroid.longitude, centroid.latitude]


def main():
    
    for tweet in sys.stdin:
        
        tweet = json.loads(tweet)
        
        if not related(tweet):
            continue
        
        #tweet['coordinates'] = geoparse(tweet)
        #if not tweet['coordinates']:
        #    continue
        
        print json.dumps(tweet, ensure_ascii=False)


if __name__ == '__main__':
    
    main()


