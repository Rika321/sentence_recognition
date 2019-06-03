#!/bin/python

from __future__ import print_function
import random
from math import log
import numpy as np
from .lm import MyModel
import pickle

class MySampler:
    def __init__(self, lm, temp = 0.6):
        self.lm = lm
        self.rnd = random.Random()
        self.temp = temp

    def sample_sentence(self, prefix = ['START', 'START'], max_length = 10):
        i = 0
        sent = prefix
        word = self.sample_next( prefix, False)
        while i <= max_length and word != "END_OF_SENTENCE":
            sent.append(word)
            word = self.sample_next(sent, True)
            i += 1
        return sent[2:]

    def sample_next(self, prev, incl_eos = True):
        """Samples a single word from context.

        Can be useful to debug the model, for example if you have a bigram model,
        and know the probability of X-Y should be really high, you can run
        sample_next([Y]) to see how often X get generated.

        incl_eos determines whether the space of words should include EOS or not.
        """
        wps = []
        tot = -np.inf # this is the log (total mass)
        for w in self.lm.freq_word:
            if not incl_eos and w == "END_OF_SENTENCE":
                continue
            if w == "UNK":
                continue
            lp = self.lm.cond_logprob_trigram_smooth(w, prev)
            wps.append([w, lp/self.temp])
            tot = np.logaddexp2(lp/self.temp, tot)
        p = self.rnd.random()
        word = self.rnd.choice(wps)[0]
        s = -np.inf # running mass
        for w,lp in wps:
            s = np.logaddexp2(s, lp)
            if p < pow(2, s-tot):
                word = w
                break
        return word



class Sampler:

    def __init__(self, lm, temp = 1.0):
        """Sampler for a given language model.

        Supports the use of temperature, i.e. how peaky we want to treat the
        distribution as. Temperature of 1 means no change, temperature <1 means
        less randomness (samples high probability words even more), and temp>1
        means more randomness (samples low prob words more than otherwise). See
        simulated annealing for what this means.
        """
        self.lm = lm
        self.rnd = random.Random()
        self.temp = temp

    def sample_sentence(self, prefix = [], max_length = 100):
        """Sample a random sentence (list of words) from the language model.

        Samples words till either EOS symbol is sampled or max_length is reached.
        Does not make any assumptions about the length of the context.
        """
        i = 0
        sent = prefix
        word = self.sample_next(sent, False)
        while i <= max_length and word != "END_OF_SENTENCE":
            sent.append(word)
            word = self.sample_next(sent)
            i += 1
        return sent

    def sample_next(self, prev, incl_eos = True):
        """Samples a single word from context.

        Can be useful to debug the model, for example if you have a bigram model,
        and know the probability of X-Y should be really high, you can run
        sample_next([Y]) to see how often X get generated.

        incl_eos determines whether the space of words should include EOS or not.
        """
        wps = []
        tot = -np.inf # this is the log (total mass)
        for w in self.lm.vocab():
            if not incl_eos and w == "END_OF_SENTENCE":
                continue
            lp = self.lm.cond_logprob(w, prev)
            wps.append([w, lp/self.temp])
            tot = np.logaddexp2(lp/self.temp, tot)
        p = self.rnd.random()
        word = self.rnd.choice(wps)[0]
        s = -np.inf # running mass
        for w,lp in wps:
            s = np.logaddexp2(s, lp)
            if p < pow(2, s-tot):
                word = w
                break
        return word


def transfer_stream(fs):
    data = []
    labels = []
    for line in fs:
        try:
            line = line.decode("UTF-8")
            (label,text) = line.strip().split("\t")
            labels.append(label)
            data.append(text)
        except:
            print(line)
    return data, labels


# def read_tsv_list(filename):
#     data = []
#     labels = []
#     for line in fs:
#         try:
#             line = line.decode("UTF-8")
#             (label,text) = line.strip().split("\t")
#             labels.append(label)
#             data.append(text)
#         except:
#             print(line)
#     return data, labels


import re
st='one two,three; four-five,    six'
#rint re.split(r'\s+|[,;.-]\s*', st)

def read_tsv_list(filename):
    try:
        result = []
        counter = 0
        with open(filename, 'r', encoding='UTF-8') as f:
            for line in f:
                (label,text) = line.strip().split("\t")
                result.append(re.split(r'\s+|[,;.-]\s*', text))
                counter += 1
        return result
    except Exception as e:
        print(e)
        return 0


if __name__ == "__main__":

    filename = "review_train_clean.tsv"
    corpus = read_tsv_list(filename)
    mymodel = MyModel(corpus)
    mymodel.fit_corpus(corpus)
    sampler = MySampler(mymodel)
    with open("super.file", "wb") as f:
        pickle.dump(sampler, f, pickle.HIGHEST_PROTOCOL)

    with open("super.file", "rb") as f:
        new_sampler = pickle.load(f)

    # print(sampler.sample_sentence(['START', 'START'],20))
    for i in range(10):
        print(i, ":", " ".join(str(x) for x in new_sampler.sample_sentence(['START', 'START'], 10)))
