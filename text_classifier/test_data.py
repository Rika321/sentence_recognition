
#!/bin/python

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import numpy as np
import sys


# Python 3 backwards compatibility tricks
if sys.version_info.major > 2:

    def xrange(*args, **kwargs):
        return iter(range(*args, **kwargs))

    def unicode(*args, **kwargs):
        return str(*args, **kwargs)


def textToTokens(text):
    """Converts input string to a corpus of tokenized sentences.

    Assumes that the sentences are divided by newlines (but will ignore empty sentences).
    You can use this to try out your own datasets, but is not needed for reading the homework data.
    """
    corpus = []
    sents = text.split("\n")
    from sklearn.feature_extraction.text import CountVectorizer
    count_vect = CountVectorizer()
    count_vect.fit(sents)
    tokenizer = count_vect.build_tokenizer()
    for s in sents:
        toks = tokenizer(s)
        if len(toks) > 0:
            corpus.append(toks)
    return corpus

def file_splitter(filename, seed = 0, train_prop = 0.7, dev_prop = 0.15,
    test_prop = 0.15):
    """Splits the lines of a file into 3 output files."""
    import random
    rnd = random.Random(seed)
    basename = filename[:-4]
    train_file = open(basename + ".train.txt", "w")
    test_file = open(basename + ".test.txt", "w")
    dev_file = open(basename + ".dev.txt", "w")
    with open(filename, 'r') as f:
        for l in f.readlines():
            p = rnd.random()
            if p < train_prop:
                train_file.write(l)
            elif p < train_prop + dev_prop:
                dev_file.write(l)
            else:
                test_file.write(l)
    train_file.close()
    test_file.close()
    dev_file.close()

def read_texts(tarfname, dname):
    """Read the data from the homework data file.

    Given the location of the data archive file and the name of the
    dataset (one of brown, reuters, or gutenberg), this returns a
    data object containing train, test, and dev data. Each is a list
    of sentences, where each sentence is a sequence of tokens.
    """
    import tarfile
    tar = tarfile.open(tarfname, "r:gz", errors = 'replace')
    for member in tar.getmembers():
        if dname in member.name and ('train.txt') in member.name:
            print('\ttrain: %s'%(member.name))
            train_txt = unicode(tar.extractfile(member).read(), errors='replace')
        elif dname in member.name and ('test.txt') in member.name:
            print('\ttest: %s'%(member.name))
            test_txt = unicode(tar.extractfile(member).read(), errors='replace')
        elif dname in member.name and ('dev.txt') in member.name:
            print('\tdev: %s'%(member.name))
            dev_txt = unicode(tar.extractfile(member).read(), errors='replace')

    from sklearn.feature_extraction.text import CountVectorizer
    count_vect = CountVectorizer()
    count_vect.fit(train_txt.split("\n"))
    tokenizer = count_vect.build_tokenizer()
    class Data: pass
    data = Data()
    data.train = []
    for s in train_txt.split("\n"):
        toks = tokenizer(s)
        if len(toks) > 0:
            data.train.append(toks)
    data.test = []
    for s in test_txt.split("\n"):
        toks = tokenizer(s)
        if len(toks) > 0:
            data.test.append(toks)
    data.dev = []
    for s in dev_txt.split("\n"):
        toks = tokenizer(s)
        if len(toks) > 0:
            data.dev.append(toks)
    print(dname," read.", "train:", len(data.train), "dev:", len(data.dev), "test:", len(data.test))
    return data


def print_table(table, row_names, col_names, latex_file = None):
    """Pretty prints the table given the table, and row and col names.

    If a latex_file is provided (and tabulate is installed), it also writes a
    file containing the LaTeX source of the table (which you can \input into your report)
    """
    try:
        from tabulate import tabulate
        row_format ="{:>15} " * (len(col_names) + 1)
        rows = map(lambda rt: [rt[0]] + rt[1], zip(row_names,table.tolist()))

        print(tabulate(rows, headers = [""] + col_names))
        if latex_file is not None:
            latex_str = tabulate(rows, headers = [""] + col_names, tablefmt="latex")
            with open(latex_file, 'w') as f:
                f.write(latex_str)
                f.close()
    except ImportError as e:
        for row_name, row in zip(row_names, table):
            print(row_format.format(row_name, *row))

def learn_myTrigram(data, verbose=True):
    from .lm import MyModel
    myModel = MyModel(data.train)
    myModel.fit_corpus(data.train)
    if verbose:
        print(myModel.uni_model)
        print("vocab:", len(myModel.vocals))
        # evaluate on train, test, and dev
        print("train:", myModel.perplexity_trigram(data.train))
        print("dev  :", myModel.perplexity_trigram(data.dev))
        print("test :", myModel.perplexity_trigram(data.test))
        from .generator import MySampler
        sampler = MySampler(myModel)
        print("sample 1: ", " ".join(str(x) for x in sampler.sample_sentence(['START', 'The'])))
        print("sample 2: ", " ".join(str(x) for x in sampler.sample_sentence(['START', 'The'])))
        print("sample 3: ", " ".join(str(x) for x in sampler.sample_sentence(['START', 'The'])))
        print("sample 4: ", " ".join(str(x) for x in sampler.sample_sentence(['START', 'The'])))
    return myModel


def Tune_myTrigram(data, verbose=True):
    from .lm import MyModel
    _apha_space =    [0.0001, 0.00001, 0.000001]
    _lambdas_space = [[0.55, 0.35, 0.1],  [0.65, 0.25, 0.1], [0.75, 0.15, 0.1] ]
    for _alpha in _apha_space:
        for _lambdas in _lambdas_space:
            print("---------------")
            print("alpha:", _alpha)
            print("lambda:", _lambdas)
            myModel = MyModel(data.train, _alpha, _lambdas)
            myModel.fit_corpus(data.train)
            print("dev  :", myModel.perplexity_trigram(data.dev, ))


if __name__ == "__main__":
    model = learn_myTrigram()
    # Tune_myTrigram(tune_data, verbose=True)
    # #tune the models using brown text
    # tune_data = read_texts("data/corpora.tar.gz", "brown")
    # Tune_myTrigram(tune_data, verbose=True)
    # dnames = ["brown", "reuters", "gutenberg"]
    # datas = []
    # models = []
    # # Learn the models for each of the domains, and evaluate it
    # for dname in dnames:
    #     print("-----------------------")
    #     print(dname)
    #     data = read_texts("data/corpora.tar.gz", dname)
    #     datas.append(data)
    #     model = learn_myTrigram(data)
    #     models.append(model)
    # #compute the perplexity of all pairs
    # n = len(dnames)
    # perp_dev = np.zeros((n,n))
    # perp_test = np.zeros((n,n))
    # perp_train = np.zeros((n,n))
    # for i in range(n):
    #     for j in range(n):
    #         perp_dev[i][j] = models[i].perplexity_trigram(datas[j].dev)
    #         perp_test[i][j] = models[i].perplexity_trigram(datas[j].test)
    #         perp_train[i][j] = models[i].perplexity_trigram(datas[j].train)
    #
    # print("-------------------------------")
    # print("x train")
    # print_table(perp_train, dnames, dnames, "table-train.tex")
    # print("-------------------------------")
    # print("x dev")
    # print_table(perp_dev, dnames, dnames, "table-dev.tex")
    # print("-------------------------------")
    # print("x test")
    # print_table(perp_test, dnames, dnames, "table-test.tex")