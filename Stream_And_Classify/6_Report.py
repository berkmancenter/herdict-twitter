"""POST reports to the Herdict server."""


import json

import redis
import requests


r = redis.StrictRedis()


def main():
    while True:
        key, data = r.brpop('5:6')
        tweet = json.loads(data)
        payload = {'report_type': 'siteInaccessible',
                   'report.url': tweet['url'],
                   'report.country.shortName': tweet['country_code'],
                   'report.sourceID': 8,  # GSOC_TWITTER
                   'report.comments': tweet['text']}
        #requests.post('http://www.herdict.org/action/ajax/plugin/report',
        #              data = payload)
        print payload


if __name__ == '__main__':
    main()


