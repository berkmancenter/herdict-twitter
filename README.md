# herdict-twitter

## Overview

[Herdict](http://www.herdict.org/) crowdsources the process of identifying web blockages.
The primary data sources are user reports submitted via the [browser add-on](http://www.herdict.org/participate/download), Tweets [@herdictreport](http://twitter.com/herdictreport), and emails to [report@herdict.org](mailto:report@herdict.org).

herdict-twitter adds a new data source to Herdict: it listens to the Twitter public timeline for users who report Internet inaccessibility but who may be unaware of Herdict.
For example, if a user Tweets "is http://www.nytimes.com/ down for anybody else?", these scripts will automatically generate and submit to Herdict a report containing the user's problematic URL, timestamp, and location.
These data update the real-time data feeds on the Herdict web site.

Here are two sample reports:

    {
      'report.country.shortName': u'CA',
      'report.comments': u'@BlackSymbiote Website links are broken - go here http://t.co/v42UYqF3xp',
      'report.url': u'http://cardsagainsthumanity.myshopify.com/',
      'report_type': 'siteInaccessible',
      'report.sourceID': 8
    }

    {
      'report.country.shortName': u'GB',
      'report.comments': u"@CloudFlare Services down? I can't access http://t.co/8CbQW17t8v neither any of my websites running on Cloudflare. Location: UK",
      'report.url': u'http://cloudflare.com',
      'report_type': 'siteInaccessible',
      'report.sourceID': 8
    }

Building herdict-twitter required collecting and manually annotating training data.
Due to Twitter's Terms of Service these data are not included in this repository; however, the remainder of herdict-twitter is licensed under the [BSD 3-Clause License](http://opensource.org/licenses/BSD-3-Clause).

## Technical Implementation

herdict-twitter connects to the Twitter Streaming API via a privileged "Restricted Track" role.
Streamed Tweets are passed through filters to eliminate retweets, non-English Tweets, and Tweets lacking location data.
Tweets that pass theses filters are then preprocessed, featurized, and classified as "Internet inaccessible" or not by a [Na&#239;ve Bayes classifier](https://en.wikipedia.org/wiki/Naive_Bayes_classifier).
Tweets deemed to be related to Internet inaccessibility are then geocoded using the [Google Geocoding API](https://developers.google.com/maps/documentation/geocoding/) and POSTed to the Herdict server endpoint.
Note that this does not violate the Google Geocoding API Terms of Service because Herdict visualizes reports using the Google Maps API.

## Directory Structure and Files

*Miscellaneous* contains one-off scripts.
Of note is a shell script to download the latest report log from Herdict and count how frequently each domain occurs.
These data inform subsequent analysis.

*Retrieve_Historical_Data* contains two R scripts to retrieve historical Tweets via the Twitter Search API and preprocess them for labelling via Amazon Mechanical Turk.
Hard-coded into the first script is the variety of nouns, verbs, and hashtags used to capture these training data.

*Stream_And_Classify* contains Python scripts that comprise the bulk of this repository.
Each script performs an independant task: streaming Tweets; filtering retweets, non-English Tweets, and Tweets lacking location data; classifying Tweets as related to Internet inaccessibility or not; geocoding Tweets, and POSTing Tweets to the Herdict server endpoint for visualization and analysis.

## Installation and Usage

Clone this repository locally and ensure that the dependencies listed below are installed and that the Redis server is running.
Then start the streaming and classifying processes in reverse order; i.e., from geocoding to streaming.

## Dependencies

The training data were collected using
[R](http://www.r-project.org/) and the
[twitteR 0.99.19](http://cran.r-project.org/web/packages/twitteR/)
library.

The streaming and classification scripts require
[Python 2.7.3](http://python.org/) with the
[tweepy 1.11](https://github.com/tweepy/tweepy),
[redis-py 2.7.1](https://github.com/andymccurdy/redis-py),
[numpy 1.6.2](http://www.numpy.org/),
[nltk 2.0.3](http://nltk.org/), and
[geopy 0.94.2](https://code.google.com/p/geopy/)
modules, as well as 
[Redis 2.14.10](http://redis.io/)

## Contributors

Code written by [Ross Petchler](mailto:ross.petchler@gmail.com) during the 2012 [Google Summer of Code](https://developers.google.com/open-source/soc/).

Project conceived and guided by [Ryan Budish](mailto:ryan@herdict.org), director of Herdict.

## Copyright and License

Copyright (c) 2012, President and Fellows of Harvard College
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

* Redistributions of source code must retain the above copyright
notice, this list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the following disclaimer in the
documentation and/or other materials provided with the distribution.
* Neither the name of the <ORGANIZATION> nor the names of its
contributors may be used to endorse or promote products derived from
this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

