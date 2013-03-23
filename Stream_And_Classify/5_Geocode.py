"""Geocode Tweets using the Google Geocoding API. Extract country data."""


import csv
import json

from pygeocoder import Geocoder, GeocoderError
import redis


with open('Data/Country_Codes.csv') as f:
    ccmap = {name.decode('UTF-8'): code for name, code in csv.reader(f)}

r = redis.StrictRedis()


def main():
    while True:
        key, data = r.brpop('4:5')
        tweet = json.loads(data)
        try:
            geodata = Geocoder.geocode(tweet['user']['location'])
            tweet['country_code'] = ccmap[geodata.country]
            r.lpush('5:6', json.dumps(tweet, ensure_ascii=False))
        except (GeocoderError, KeyError):
            continue


if __name__ == '__main__':
    main()


