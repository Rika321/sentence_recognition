#!/bin/python

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from collections import defaultdict
from math import log
import sys
from nltk.probability import LidstoneProbDist

# Python 3 backwards compatibility tricks
if sys.version_info.major > 2:
    def xrange(*args, **kwargs):
        return iter(range(*args, **kwargs))

    def unicode(*args, **kwargs):
        return str(*args, **kwargs)

class MyModel:
    def __init__(self, corpus, _apha = 1e-06, _lambdas = [0.55,0.35,0.1]):
        self._apha = _apha
        self._lambdas = _lambdas
        self.uni_model = defaultdict(float)
        self.bi_model = defaultdict(float)
        self.tri_model = defaultdict(float)
        self.freq_word = self.get_freq_word(corpus)
        self.vocals    = self.get_vocals(corpus)
        self.tot = 0.0

    def get_vocals(self, corpus):
        freq_count = defaultdict(float)
        for s in corpus:
            for word in s:
                freq_count[word] += 1
        result = set()
        for k,v in freq_count.items():
            result.add(k)
        result.add("START")
        result.add("END_OF_SENTENCE")
        result.add("UNK")
        return result


    def get_freq_word(self, corpus):
        freq_count = defaultdict(float)
        for s in corpus:
            for word in s:
                freq_count[word] += 1
        result = set()
        for k,v in freq_count.items():
            if v > 4:
                result.add(k)
        result.add("START")
        result.add("END_OF_SENTENCE")
        result.add("UNK")
        return result

    def prepare_corpus(self, corpus):
        clean_corpus = []
        for s in corpus:
            new_s = [word if word in self.freq_word else "UNK" for word in s]
            clean_corpus.append(new_s)
        return clean_corpus

    def fit_sentence_unigram(self, sentence):
        pd = sentence + ["END_OF_SENTENCE"]
        for i in range(len(pd)):
            unigram = (pd[i])
            self.uni_model[unigram] += 1
            self.tot += 1

    def fit_sentence_bigram(self, sentence):
        pd = ["START"] + sentence + ["END_OF_SENTENCE"]
        for i in range(len(pd)-1):
            bigram = (pd[i], pd[i+1])
            self.bi_model[bigram] += 1
            if pd[i] == "START":
                self.uni_model[('START')] += 1

    def fit_sentence_trigram(self, sentence):
        pd = ["START"] + ["START"] + sentence + ["END_OF_SENTENCE"]
        for i in range(len(pd)-2):
            trigram = (pd[i], pd[i+1], pd[i+2])
            self.tri_model[trigram] += 1
            if pd[i] == "START" and pd[i+1] == "START":
                self.bi_model[('START', 'START')] += 1

    def fit_corpus(self, corpus):
        clean_corpus = self.prepare_corpus(corpus)
        for s in clean_corpus:
            self.fit_sentence_unigram(s)
            self.fit_sentence_bigram(s)
            self.fit_sentence_trigram(s)


    def perplexity_trigram(self, corpus):
        return pow(2.0, self.entropy_trigram(corpus))

    def entropy_trigram(self, corpus):
        num_words = 0.0
        sum_logprob = 0.0
        for s in corpus:
            pd = ["START"] + ["START"] + s + ["END_OF_SENTENCE"]
            num_words += len(s) + 1 # for EOS
            sum_logprob += self.logprob_sentence_trigram(pd)
        return -(1.0/num_words)*(sum_logprob)

    def logprob_sentence_trigram(self, sentence):
        p = 0.0
        for i in range(2, len(sentence)):
            p += self.cond_logprob_trigram_smooth(sentence[i], sentence[:i])
        return p


    def cond_logprob_bigram_smooth(self, word, prev):
        bigram   = (prev[-1], word)
        unigram  = (prev[-1])
        if bigram in self.bi_model and unigram in self.uni_model:
            return log(self.bi_model[bigram] + self._apha, 2) - log(self.uni_model[unigram] + self._apha*len(self.freq_word), 2)
        else:
            return log(self._apha, 2) - log(self._apha*len(self.freq_word), 2)


    def cond_logprob_trigram_smooth(self, word, prev):
        trigram = (prev[-2], prev[-1], word)
        bigram  = (prev[-2], prev[-1])
        unigram = (prev[-2])
        if trigram in self.tri_model and bigram in self.bi_model and unigram in self.uni_model:

            q1 = (self.tri_model[trigram]+ self._apha)/ (self.bi_model[bigram] + self._apha*len(self.freq_word))  * self._lambdas[0]
            q2 = (self.bi_model[bigram]  + self._apha)/ (self.uni_model[unigram] + self._apha*len(self.freq_word))* self._lambdas[1]
            q3 = (self.uni_model[unigram]  + self._apha)/ (self.tot + self._apha*len(self.freq_word))               * self._lambdas[2]
            return log(q1+q2+q3, 2)
        else:
            #return self.lbackoff - log(self.tot, 2)
            return log(self._apha, 2) - log(self._apha*len(self.freq_word), 2)



class LangModel:

    def fit_corpus(self, corpus):
        """Learn the language model for the whole corpus.
        The corpus consists of a list of sentences."""
        for s in corpus:
            self.fit_sentence(s)
        self.norm()

    def perplexity(self, corpus):
        """Computes the perplexity of the corpus by the model.

        Assumes the model uses an EOS symbol at the end of each sentence.
        """
        return pow(2.0, self.entropy(corpus))

    def entropy(self, corpus):
        num_words = 0.0
        sum_logprob = 0.0
        for s in corpus:
            num_words += len(s) + 1 # for EOS
            sum_logprob += self.logprob_sentence(s)
        return -(1.0/num_words)*(sum_logprob)

    def logprob_sentence(self, sentence):
        p = 0.0
        for i in xrange(len(sentence)):
            p += self.cond_logprob(sentence[i], sentence[:i])
        p += self.cond_logprob('END_OF_SENTENCE', sentence)
        return p

    # required, update the model when a sentence is observed
    def fit_sentence(self, sentence): pass

    # optional, if there are any post-training steps (such as normalizing probabilities)
    def norm(self): pass

    # required, return the log2 of the conditional prob of word, given previous words
    def cond_logprob(self, word, previous): pass

    # required, the list of words the language model suports (including EOS)
    def vocab(self): pass



class Unigram(LangModel):
    def __init__(self, backoff=0.00001):
        self.model = dict()
        self.lbackoff = log(backoff, 2)

    def inc_word(self, w):
        if w in self.model:
            self.model[w] += 1.0
        else:
            self.model[w] = 1.0

    def fit_sentence(self, sentence):
        for w in sentence:
            self.inc_word(w)
        self.inc_word('END_OF_SENTENCE')

    def norm(self):
        """Normalize and convert to log2-probs."""
        tot = 0.0
        for word in self.model:
            tot += self.model[word]
        ltot = log(tot, 2)
        for word in self.model:
            self.model[word] = log(self.model[word], 2) - ltot

    def cond_logprob(self, word, previous):
        if word in self.model:
            return self.model[word]
        else:
            return self.lbackoff

    def vocab(self):
        return self.model.keys()
