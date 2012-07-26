"""
"""


import codecs
import csv
import itertools
import json
import locale
import string
import sys

import nltk


# Wrap sys.stdout into a StreamWriter to allow writing Unicode.
sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)


def preprocess(text, min_word_length=3):
    
    # Strip leading and trailing whitespace, lowercase, split on spaces.
    text = text.strip().lower().split()
    
    # Remove non-hashtag tweet entities.
    #text = [w for w in text if not w.startswith(('http', '@'))]
    
    # Tokenize.
    text = nltk.word_tokenize(' '.join(text))
    
    # Remove punctuation.
    text = ' '.join(text)
    text = ''.join(l for l in text if not l in string.punctuation)
    text = text.split()
    
    # Remove English stopwords.
    text = [w for w in text if not w in nltk.corpus.stopwords.words('english')]
    
    # Remove short words.
    text = [w for w in text if len(w) >= min_word_length]
    
    # Stem words.
    text = [nltk.PorterStemmer().stem(w) for w in text]
    
    return text


def extract_features(document):
    """Extracts features from a document.
    
    Note that this function requires ``features'', a global object that
    is the set of preprocessed tokens that appear in all documents in
    the training data set. Ideally this object would be passed as an
    argument (moving all the code at the top of this script inside the
    __main__ function), but the nltk.classify.apply_features() function
    does not pass arguments to the featurizing function it applies.
    
    Args:
        document: The list of preprocessed tokens that appear in the
            document.

    Returns:
        A dictionary whose keys are the features from the ``features''
        set, and whose values are either True or False, depending on
        whether the document contains those features.
    """
    document_tokens = set(document)
    document_features = dict()
    for token in features:
        document_features[token] = token in document_tokens
    return document_features


with open('/home/rosspetchler/GSoC/Classifier_Training_Data.csv') as f:
    training = [(t[0], int(t[1])) for t in csv.reader(f)]

training = [(preprocess(t[0]), t[1]) for t in training]

# Create a list of features. For now, just use words.
features = itertools.chain.from_iterable([w for w, j in training])
features = set(nltk.FreqDist(features).keys())

training = nltk.classify.apply_features(extract_features, training)

classifier = nltk.NaiveBayesClassifier.train(training)

#classifier.show_most_informative_features(32)


def main():
    
    for tweet in sys.stdin:
        tweet = json.loads(tweet)
        tweet = tweet['text']
        judgement = classifier.classify(extract_features(preprocess(tweet)))
        if judgement == 1:
            print tweet




"""
if status.has_key('retweeted_status'):
    retweet = {'_id'  : status['retweeted_status']['id'],
               'json' : status['retweeted_status']}
    # insert to DB...

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
#   status['detected_lang'] = detected_lang if reliable else None
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
"""


if __name__ == '__main__':
    
    main()


