"""
"""


import collections
import csv
import itertools
import json
import locale
import string

import nltk


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


def evaluate_classifier(training_data_set, testing_data_set, feature_extraction_function):
    
    training = nltk.classify.apply_features(feature_extraction_function, training_data_set)
    testing = nltk.classify.apply_features(feature_extraction_function, testing_data_set)
    
    classifier = nltk.NaiveBayesClassifier.train(training)
    refsets = collections.defaultdict(set)
    testsets = collections.defaultdict(set)
    
    for i, (features, label) in enumerate(testing):
        refsets[label].add(i)
        observed = classifier.classify(features)
        testsets[observed].add(i)
    
    print 'Accuracy:', nltk.classify.util.accuracy(classifier, testing)
    
    print ' 1 precision:', nltk.metrics.precision(refsets[1], testsets[1])
    print ' 1 recall:   ', nltk.metrics.recall(refsets[1], testsets[1])
    print ' 1 F-measure:', nltk.metrics.f_measure(refsets[1], testsets[1])
    print '-1 precision:', nltk.metrics.precision(refsets[-1], testsets[-1])
    print '-1 recall:   ', nltk.metrics.recall(refsets[-1], testsets[-1])
    print '-1 F-measure:', nltk.metrics.f_measure(refsets[-1], testsets[-1])
    
    classifier.show_most_informative_features()


def main():
    
    with open('/home/rosspetchler/GSoC/Classifier_Training_Data.csv') as f:
        trained_data = [(t[0], int(t[1])) for t in csv.reader(f)]
    
    trained_data = [(preprocess(t[0]), t[1]) for t in trained_data]
    
    cutoff = len(trained_data) * 4/5
    
    training, testing = trained_data[:cutoff], trained_data[cutoff:]
    
    print 'Training on {} tweets.'.format(len(training))
    print 'Testing on {} tweets.'.format(len(testing))
    
    def word_feats(words):
        return dict((word, True) for word in words)
    
    print 'Evaluating single word features.'
    evaluate_classifier(training, testing, word_feats)
    
    word_freq_dist = nltk.probability.FreqDist()
    label_word_freq_dist = nltk.probability.ConditionalFreqDist()
    
    for features, judgement in training + testing:
        for feature in features:
            word_freq_dist.inc(feature)
            label_word_freq_dist[judgement].inc(feature)
    
    include_count = label_word_freq_dist[1].N()
    exclude_count = label_word_freq_dist[-1].N()
    total_count = include_count + exclude_count
    
    word_scores = {}
    for word, frequency in word_freq_dist.iteritems():
        include_score = nltk.metrics.BigramAssocMeasures.chi_sq(
                            label_word_freq_dist[1][word],
                            (frequency, include_count), total_count)
        exclude_score = nltk.metrics.BigramAssocMeasures.chi_sq(
                            label_word_freq_dist[-1][word],
                            (frequency, exclude_count), total_count)
        word_scores[word] = include_score + exclude_score
    
    high_information_words = sorted(word_scores.iteritems(),
                                    key=lambda (w, j): j,
                                    reverse = True)[:8000]
    bestwords = set([word for word, judgement
                                  in high_information_words])
    
    def high_information_features(words):
        return dict((word, True) for word in words
                    if word in bestwords)
    
    print 'Evaluating high information features.'
    evaluate_classifier(training, testing, high_information_features)
    
    def best_bigram_word_feats(words, score_fn=nltk.metrics.BigramAssocMeasures.chi_sq, n=200):
        bigram_finder = nltk.collocations.BigramCollocationFinder.from_words(words)
        bigrams = bigram_finder.nbest(score_fn, n)
        d = dict((bigram, True) for bigram in bigrams)
        d.update(high_information_features(words))
        return d
    
    print 'evaluating best words + bigram chi_sq word features'
    evaluate_classifier(training, testing, best_bigram_word_feats)


if __name__ == '__main__':
    
    main()


