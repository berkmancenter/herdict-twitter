"""

http://streamhacker.com/2010/05/10/text-classification-sentiment-analysis-naive-bayes-classifier/
http://streamhacker.com/2010/05/24/text-classification-sentiment-analysis-stopwords-collocations/
http://streamhacker.com/2010/06/16/text-classification-sentiment-analysis-eliminate-low-information-features/

http://www.laurentluce.com/posts/twitter-sentiment-analysis-using-python-and-nltk/

http://www.nytimes.com/2012/05/29/world/asia/china-cracks-down-on-its-cagey-web-critics.html
"""


import pymongo


# Import parameters.
with open('/home/twitter-data/docs/parameters.json') as f:
    par = json.loads(f.read())


# Connect to MongoDB.
conn = pymongo.Connection(par['server_name'])
db = getattr(conn, par['database_name'])


cursor = db.statuses.find({'censorship' : {'$exists' : True}})

print 'Training data contains {} elements.'.format(cursor.count())

censorship_features = []
noncensorship_features = []

for document in cursor:
    if document['censorship'] == 'y':
        censorship_features.extend(document['preprocessed'])
    if document['censorship'] == 'n':
        noncensorship_features.extend(document['preprocessed'])





import nltk.classify.util
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import movie_reviews
 
 
classifier = NaiveBayesClassifier.train(trainfeats)
print 'accuracy:', nltk.classify.util.accuracy(classifier, testfeats)
classifier.show_most_informative_features()



