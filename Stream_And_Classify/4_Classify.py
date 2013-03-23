"""Classify whether Tweets refer to Internet inaccessibility."""


import csv
import itertools
import json
import operator
import re
import string

import nltk
import redis


r = redis.StrictRedis()


with open('Parameters.json') as f:
    p = json.load(f)

with open('Data/HTML_Character_Entities.csv') as f:
    character_entities = dict(csv.reader(f))

with open('Data/Contractions.csv') as f:
    contractions = dict(csv.reader(f))

# Duplicate all contraction mappings without apostrophies. For example,
# both "can't" and "cant" map to "can not".
for k in contractions.keys():  # Iterate over keys to avoid RuntimeError
    contractions[k.replace("'", '')] = contractions[k]

# Dictionary adapted from: http://www.noslang.com/dictionary/full/.
with open('Data/Slang_Dictionary.csv') as f:
    slang = dict(csv.reader(f))


def preprocess(text, minlen=3, negators=('cannot', 'never', 'no', 'not'),
               prefixes=('emo:', 'punc:', 'not:', '@', '#', 'http')):
    """
    """
    
    # Unescape HTML character entities.
    for i in character_entities.iteritems():
        text = text.replace(*i)
    
    # Remove ellipses.
    text = re.sub("\.{2,}", " ", text)
    
    # Featurize emoticons.
    text = re.sub('(:|=)-?[\(\[{<@c]+', ' emo:sad ', text)
    text = re.sub('[:;=8xXB][-o^c]?[\)\]}>D3]+', ' emo:happy ', text)
    
    # Featurize exclamatory and interrogative punctuation.
    text = text.replace('!', ' punc:exclamation ')
    text = text.replace('?', ' punc:question ')
    
    text = text.strip().lower()
    text = ' '.join(text.split())  # Normalize whitespace characters.
    
    # Expand or delete contractions.
    for i in contractions.iteritems():
        text = text.replace(*i)
    
    # Remove leading and trailing punctuation.
    text = [w.strip(string.punctuation) if not w.startswith(prefixes)
            else w for w in text.split()]
    
    # Replace slang words.
    text = [slang.get(w, w).lower().split() if not w.startswith(prefixes)
            else [w] for w in text]
    text = itertools.chain.from_iterable(text)
    
    # Tokenize words in tweet.
    text = [nltk.word_tokenize(w) if not w.startswith(prefixes)
            else [w] for w in text]
    text = itertools.chain.from_iterable(text)
    
    # Replace negation tokens with not:{}. Inspired by Pang and Lee's
    # work on sentiment analysis.
    text = ' '.join(text)
    for i in negators:
        text = text.replace(' {} '.format(i), ' not:')
    text = text.split()
    
    # Remove short words.
    text = [w for w in text if w.startswith(prefixes) or len(w) >= minlen]
    
    # Remove English stopwords.
    text = [w for w in text if w.startswith(prefixes)
            or w not in nltk.corpus.stopwords.words('english')]
    
    # Stem words.
    text = [nltk.PorterStemmer().stem(w) if not w.startswith(prefixes)
            else w for w in text]
    
    # Add bigrams.
    text.extend(nltk.bigrams(text))
    
    return text


def extract_features(tweet):
    
    # Coerce judgement type. Only used during classifier training.
    if 'label' in tweet:
        tweet['label'] = int(tweet['label'])
    
    # Preprocess tweet text.
    tweet['preprocessed'] = preprocess(tweet['text'])
    
    # Determine tweet source, broadly (either web or non-web).
    broad_source = 'web' if tweet['source'] == 'web' else 'non-web'
    broad_source = 'source_broad:{}'.format(broad_source)
    
    # Determine tweet source, specifically (device or platform source).
    # Remove HTML tags.
    specific_source = nltk.clean_html(tweet['source'])
    # Remove non-ASCII characters.
    specific_source = "".join(i for i in specific_source if ord(i) < 128)
    specific_source = specific_source.replace(' ', '_')
    specific_source = 'source_specific:{}'.format(specific_source)
    
    # Extract textual and non-textual tweet features.
    tweet['features'] = tweet['preprocessed']
    tweet['features'].extend([specific_source, broad_source])
    
    return tweet


def main():
    
    with open('Data/Training_Data_Labelled.csv') as f:
        training_data = [extract_features(l) for l in csv.DictReader(f)]
    
    # Count occurances of each feature in the training data set, both
    # overall and by label.
    feature_freq_dist = nltk.probability.FreqDist()
    label_feature_freq_dist = nltk.probability.ConditionalFreqDist()
    for tweet in training_data:
        for feature in tweet['features']:
            feature_freq_dist.inc(feature)
            label_feature_freq_dist[tweet['label']].inc(feature)
    
    # Compute how frequently each feature occurs under each label.
    include_count = label_feature_freq_dist[1].N()
    exclude_count = label_feature_freq_dist[-1].N()
    # Compute the total number of times all features occur.
    total_count = include_count + exclude_count
    
    # Compute information gain for each feature. Information gain meaures
    # how frequently a feature occurs in one particular class relative to
    # all other classes.
    # In this case, use the Chi-squared statistic between the overall
    # frequency of a feature (feature_freq_dist) and its frequency within
    # a class (label_feature_freq_dist).
    feature_scores = {}
    for feature, frequency in feature_freq_dist.iteritems():
        include_score = nltk.metrics.BigramAssocMeasures.chi_sq(
                label_feature_freq_dist[1][feature],
                (frequency, include_count), total_count)
        exclude_score = nltk.metrics.BigramAssocMeasures.chi_sq(
                label_feature_freq_dist[-1][feature],
                (frequency, exclude_count), total_count)
        feature_scores[feature] = include_score + exclude_score
    
    # Sort features by information gain and subset the most informative
    # ones to reduce the dimensionality of the data set.
    high_information_features = sorted(feature_scores.iteritems(),
        key=operator.itemgetter(1), reverse=True)[:3000]
    high_information_features = set(feature for feature, feature_score
        in high_information_features)
    
    def most_informative_features(tweet):
        return ({f: True for f in tweet['preprocessed']
                 if f in high_information_features}, tweet['label'])

    training_data = nltk.classify.apply_features(most_informative_features, training_data)
    classifier = nltk.NaiveBayesClassifier.train(training_data)
    
    while True:
        key, data = r.brpop('3:4')
        tweet = json.loads(data)
        tweet = extract_features(tweet)
        featureset = {f: True for f in tweet['preprocessed']}
        prob = classifier.prob_classify(featureset).prob(1)
        if prob >= p['confidence_level']:
            r.lpush('4:5', json.dumps(tweet, ensure_ascii=False))


if __name__ == '__main__':
    
    main()


