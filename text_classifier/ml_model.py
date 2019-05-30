#!/bin/python
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn import preprocessing
from flask import Flask, request
import numpy as np
from scipy.sparse import vstack
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import PredefinedSplit
from sklearn.feature_selection import SelectKBest, chi2
from sklearn import metrics
from joblib import dump, load
from collections import defaultdict
import random
app = Flask(__name__)


def read_files(trainname):
    """Read the on the training data
    """
    class Data: pass
    sentiment = Data()
    print("-- train data")
    sentiment.train_data, sentiment.train_labels = read_tsv(trainname)
    # print("-- dev   data")
    # sentiment.dev_data, sentiment.dev_labels = read_tsv(devname)
    return sentiment


def transform_data(sentiment, model_name):
    print("-- transforming data and labels")
    try:
        cv = load(model_name)
        print("continue to use cv model!")
    except:
        cv = TfidfVectorizer(ngram_range=(1,2))
        print("create to new cv model!")
    sentiment.trainX = cv.fit_transform(sentiment.train_data)
    sentiment.le = preprocessing.LabelEncoder()
    sentiment.le.fit(sentiment.train_labels)
    sentiment.target_labels = sentiment.le.classes_
    sentiment.trainy = sentiment.le.transform(sentiment.train_labels)
    dump(cv, model_name)

def select_feature(sentiment, model_name):
    try:
        sk = load(model_name)
        print("continue to use sk model!")
    except:
        sk = SelectKBest(chi2, k=4000)
        print("create to new sk model!")
    sk.fit(sentiment.trainX, sentiment.trainy)
    sentiment.trainX_select = sk.transform(sentiment.trainX)
    dump(sk, model_name)

def train_classifier(X, y, model_name):
    """Train a classifier using the given training data.

    Trains logistic regression on the input data with default parameters.
    """
    try:
        lr = load(model_name)
        print("continue to use lr model!")
    except:
        lr = LogisticRegression(random_state=0, C=3, solver='lbfgs', max_iter=10000, warm_start=True)
        print("create to new lr model!")
    lr.fit(X,y)
    yp = lr.predict(X)
    acc = metrics.accuracy_score(y, yp)
    dump(lr, model_name)
    print("train finish", acc)
    return acc



def evaluate(X, yt, cls, name='data'):
    """Evaluated a classifier on the given labeled data using accuracy."""
    yp = cls.predict(X)
    acc = metrics.accuracy_score(yt, yp)
    print("  Accuracy on %s  is: %s" % (name, acc))


def get2Gram(sentence):
    result = []
    word_list = sentence.split(" ")
    for word in word_list:
        result.append([word])
    for i in range(len(word_list)-1):
        result.append([word_list[i], word_list[i+1]])
    return result


def explain_grams(sentence, cv_model_name, sk_model_name, lr_model_name):
    try:
        cv = load(cv_model_name)
        sk = load(sk_model_name)
        lr = load(lr_model_name)
        grams = get2Gram(sentence)
        gram_dict = defaultdict(float)
        for gram in grams:
            gram_ = cv.transform(gram)
            gram_ = sk.transform(gram_)
            score = lr.decision_function(gram_)[0] - lr.fit_intercept
            gram_str = ""
            for w in gram:
                if gram_str == "":
                    gram_str += w
                else:
                    gram_str += " "+w
            gram_dict[gram_str] = score
        print(sentence)
        return dict(gram_dict)
    except Exception as e:
        print("ERROR",e)
        return None



def predict(sentence, cv_model_name, sk_model_name, lr_model_name):
    X = [sentence]
    label_dict = {0:"NEGATIVE", 1:"POSITIVE"}
    try:
        cv = load(cv_model_name)
        sk = load(sk_model_name)
        lr = load(lr_model_name)
        X = cv.transform(X)
        X = sk.transform(X)
        return [label_dict[lr.predict(X)[0]], lr.decision_function(X)]
    except Exception as e:
        print(e)
        return ["NEGATIVE",None] if random.random() > 0.5 else ["POSITIVE",None]




def read_unlabeled(tarfname, sentiment):
    """Reads the unlabeled data.

    The returned object contains three fields that represent the unlabeled data.

    data: documents, represented as sequence of words
    fnames: list of filenames, one for each document
    X: bag of word vector for each document, using the sentiment.vectorizer
    """
    import tarfile
    tar = tarfile.open(tarfname, "r:gz")
    class Data: pass
    unlabeled = Data()
    unlabeled.data = []

    unlabeledname = "unlabeled.tsv"
    for member in tar.getmembers():
        if 'unlabeled.tsv' in member.name:
            unlabeledname = member.name

    print(unlabeledname)
    tf = tar.extractfile(unlabeledname)
    for line in tf:
        line = line.decode("utf-8")
        text = line.strip()
        unlabeled.data.append(text)

    unlabeled.X = sentiment.count_vect.transform(unlabeled.data)
    print(unlabeled.X.shape)
    tar.close()
    return unlabeled

def read_tsv(fname):
    data = []
    labels = []
    with open(fname, 'r', encoding='UTF-8') as tf:
        for line in tf:
            try:
                (label,text) = line.strip().split("\t")
                labels.append(label)
                data.append(text)
            except:
                print(line)
    return data, labels

if __name__ == "__main__":
    print("Reading data")
    tarfname = "sentiment.tar.gz"
    filename = "labeled_collection.tsv"

    cv_model_name = "cv.joblib"
    sk_model_name = "sk.joblib"
    lr_model_name = "lr.joblib"

    sentiment = read_files(filename)
    print("\nTraining classifier")
    transform_data(sentiment, cv_model_name)
    select_feature(sentiment, sk_model_name)
    train_classifier( sentiment.trainX_select, sentiment.trainy,lr_model_name)

    #sentence = "food is very bad"
    sentence = "service is very awesome"
    print("prediction result:", predict(sentence, cv_model_name, sk_model_name,lr_model_name))
