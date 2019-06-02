#dev:

# data statistics
# train and dev and test
# class tag: plain text of bi-label
# keywords: dict 前多少unigram & frequency


# performance statistics
# train and dev
# accuracy, precision, recall, F1_score: assume the model


from .ml_model import *
from sklearn.metrics import precision_score
import numpy as np
import sklearn
from collections import defaultdict
from sklearn.datasets import make_classification
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, classification_report, confusion_matrix
#
# X, y = make_classification(n_samples=100, n_informative=10, n_classes=3)
# sss = StratifiedShuffleSplit(y, n_iter=1, test_size=0.5, random_state=0)
# for train_idx, test_idx in sss:
#     X_train, X_test, y_train, y_test = X[train_idx], X[test_idx], y[train_idx], y[test_idx]
#     svc.fit(X_train, y_train)
#     y_pred = svc.predict(X_test)

def precisionScore(result,y_pred, y_label): #, modelName, datasetType):
    pScore = precision_score(y_pred, y_label)
    result['PresicionScore'] = pScore


def RecallScore(result,y_pred, y_label): #, modelName, datasetType):
    rScore = recall_score(y_pred, y_label)
    result['RecallScore'] = rScore

def AccuracyScore(result,y_pred, y_label): #, modelName, datasetType):
    aScore = accuracy_score(y_pred, y_label)
    result['AccuracyScore'] = aScore
    # result.update({'AccuracyScore', aScore})

def F1Score(result,y_pred, y_label): #, modelName, datasetType):
    fScore = f1_score(y_pred, y_label)
    # result.update({'F1Score', fScore})
    result['F1Score'] = fScore

def classTag(filename):
    classTagDict = {}
    y = sentiment.trainy
    sorted(y)
    tag1 = y[0]
    tag2 = y[-1]
    freq1 = 0
    freq2 = 0
    for i in range(len(y)):
        if y[i] == tag1:
            freq1+=1
        elif y[i] == tag2:
            freq2+=1
    classTagDict.update({tag1, freq1}, {tag2, freq2})
    return classTagDict

def keywords(filename):
    X = sentiment.trainX_select
    from wordcloud import WordCloud
    wordcloud = WordCloud(background_color="white",width=1000, height=860, margin=2).generate(X)
    wordcloud.to_file('wordCloud.png')
    # width,height,margin可以设置图片属性
    # generate 可以对全部文本进行自动分词
    # 通过font_path参数来设置字体集
    # background_color参数为设置背景颜色,默认颜色为黑色

def dev_statistics(filename, cv_model_name, sk_model_name, lr_model_name):
    try:
        print("evaluate!!!!")
        result = defaultdict(float)
        tag_dict = defaultdict(int)
        sentiment = read_files(filename)
        lr = load(lr_model_name)
        transform_data(sentiment, cv_model_name)
        select_feature(sentiment, sk_model_name)
        y_dev = sentiment.trainy
        X_dev = sentiment.trainX_select
        y_pred = []
        for idx,x in enumerate(X_dev):
            y = lr.predict(x)[0]
            tag_dict[sentiment.train_labels[idx]] += 1
            y_pred.append(y)
        precisionScore(result,y_pred, y_dev)
        AccuracyScore(result,y_pred, y_dev)
        RecallScore(result,y_pred, y_dev)
        F1Score(result,y_pred, y_dev)
        result["tag"] = tag_dict
        print(result)
        return dict(result)
    except Exception as e:
        print(e)
        return None

def dev_statistics_sentiment(fs, cv_model_name, sk_model_name, lr_model_name):
    try:
        print("evaluate111!!!!")
        result = defaultdict(float)
        tag_dict = defaultdict(int)
        sentiment = read_my_file_stream(fs)
        lr = load(lr_model_name)
        transform_data(sentiment, cv_model_name)
        select_feature(sentiment, sk_model_name)
        y_dev = sentiment.trainy
        X_dev = sentiment.trainX_select
        y_pred = []
        for idx,x in enumerate(X_dev):
            y = lr.predict(x)[0]
            tag_dict[sentiment.train_labels[idx]] += 1
            y_pred.append(y)
        precisionScore(result,y_pred, y_dev)
        AccuracyScore(result,y_pred, y_dev)
        RecallScore(result,y_pred, y_dev)
        F1Score(result,y_pred, y_dev)
        result["tag"] = tag_dict
        print(result)
        return dict(result)
    except Exception as e:
        print(e)
        return None
