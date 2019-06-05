from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.files.base import ContentFile
from django.core.files import File
import random
from .file_processing import *
from .models import *
from .ml_model import *
from .dev_function import *
from django import forms
import os
import shutil
from django.http import JsonResponse
from .generator import *
import json

def get_datasets(isTrained=True):
    print(os.listdir("data"))
    datasets = [""]
    try:
        if isTrained:
            for dataset_name in os.listdir("data"):
                if dataset_name[-10:]!="_untrained":
                    datasets.append(dataset_name)
        else:
            for dataset_name in os.listdir("data"):
                if dataset_name[-10:]=="_untrained":
                    datasets.append(dataset_name)
    except:
        pass
    return datasets

def get_dataname(devname):
    name = None
    try:
        name = devname.split("/")[1]
        # print(name)
        # print(name not in os.listdir("data"))
        if name not in os.listdir("data") and name[:-10] not in os.listdir("data"):
            return None
        return name
    except:
        return None

def apply_model(request):
    template = loader.get_template('index.html')
    devname    = "data/"+request.POST.get('sel_data')
    add_save_my_session('devname',devname)
    mode = load_my_session('mode')
    devname = load_my_session('devname')
    mode = load_my_session('mode')
    random_sentence_list = []
    total_sample, classes_ = 0, None
    try:
        total_sample, classes_ = count_labeled_examples(devname+"/labeled_collection.tsv")
        le_model_name = devname+"/le.joblib"
        le = load(le_model_name)
        classes_=le.classes_
        trigram_model_name = devname+"/trigram.file"
        with open(trigram_model_name, "r") as f:
            for line in f:
                random_sentence_list.append(line.strip())
    except:
        pass
    context = {
        'classes_':classes_,
        'sentence_list': random_sentence_list,
        'devname': None if devname is None else devname[5:],
        'total_sample' : total_sample,
        'label': None,
        'mode' : mode,
        'data_name': get_dataname(devname),
        'dataset_name': get_datasets(mode == "eval_mode" or mode == "pred_mode"),
    }
    return HttpResponse(template.render(context, request))

# def helper(dev):
#     ddd

def get_company():
    companies = []
    with open("data_fixed/company.file", "r") as f:
        for line in f:
            companies.append(line.strip())
    return companies


def simple_train(request):
    template = loader.get_template('index.html')
    mode = load_my_session('mode')
    devname = load_my_session('devname') #request.session['devname']
    try:
        #bag of word
        filename = devname+"/labeled_collection.tsv"
        total_sample, classes_ = total_sample, classes_ = count_labeled_examples(devname+"/labeled_collection.tsv")
        old_name = devname
        try:
            os.mkdir(devname[:-10])
        except:
            shutil.rmtree(devname[:-10])
            os.mkdir(devname[:-10])
        devname = devname[:-10]
        add_save_my_session('devname',devname)
            # raise Exception('Invalide File')
        trigram_model_name = devname+"/trigram.file"
        old_trigram_model_name = old_name+"/trigram.file"
        corpus = read_tsv_list(filename)
        mymodel = MyModel(corpus)
        mymodel.fit_corpus(corpus)
        sampler = MySampler(mymodel)
        with open(trigram_model_name, "a+") as f:
            for i in range(50):
                random_sentence = " ".join(sampler.sample_sentence(['START', 'START'], 10))
                f.write(random_sentence+"\n")
        cv_model_name = devname+"/cv.joblib"
        le_model_name = devname+"/le.joblib"
        sk_model_name = devname+"/sk.joblib"
        lr_model_name = devname+"/lr.joblib"
        sentiment = read_files(filename)
        print("\nTraining classifier")
        transform_data(sentiment,cv_model_name, le_model_name)
        select_feature(sentiment,sk_model_name)
        acc = train_classifier( sentiment.trainX_select, sentiment.trainy, lr_model_name)
        dev_stat_ = train_statistics(sentiment, lr_model_name)
        le = load(le_model_name)
        classes_=le.classes_
        topA_val,topA_name,topB_val,topB_name = topKsignificance(20, cv_model_name,sk_model_name,lr_model_name,le_model_name)
        context = {
            'classes_':classes_,
            'sentence_list': [],
            'topA_val': topA_val,
            'topA_name': topA_name,
            'topB_val': topB_val,
            'topB_name': topB_name,
            'PresicionScore':dev_stat_['PresicionScore'],
            'F1Score':dev_stat_['F1Score'],
            'total_sample' : total_sample,
            'devname': devname,
            "train_acc" : acc,
            'mode' : mode,
            'label': None,
            'data_name':get_dataname(devname),
            'dataset_name': get_datasets(mode == "eval_mode" or mode == "pred_mode"),
        }
        return HttpResponse(template.render(context, request))
    except Exception as e:
        print(e)
        context = {
            'devname': devname,
            'total_sample' : None,
            'mode' : mode,
            'label': None,
            'data_name':get_dataname(devname),
            'dataset_name': get_datasets(mode == "eval_mode" or mode == "pred_mode"),
        }
        return HttpResponse(template.render(context, request))



def simple_add(request):
    template = loader.get_template('index.html')
    mode = load_my_session('mode')
    devname = load_my_session('devname')
    total_sample, classes_ = 0,[]
    random_sentence_list = []
    try:
        sentence = request.POST.get('sentence')
        if sentence == "":
            raise("sentence None")
        label    = request.POST.get('label')
        filename = devname+"/labeled_collection.tsv"
        counter = transfer_one_line(filename, sentence, label)
        total_sample, classes_ = count_labeled_examples(devname+"/labeled_collection.tsv")
        trigram_model_name = devname+"/trigram.file"
        with open(trigram_model_name, "r") as f:
            for line in f:
                random_sentence_list.append(line.strip())
    except:
        pass
    context = {
        'sentence_list':random_sentence_list,
        'classes_': classes_,
        'total_sample' : total_sample,
        'mode' : mode,
        'label': None,
        'data_name':get_dataname(devname),
        'dataset_name': get_datasets(mode == "eval_mode" or mode == "pred_mode"),
    }
    return HttpResponse(template.render(context, request))


def simple_eval(request):
    template = loader.get_template('index.html')
    mode = load_my_session('mode')
    devname = load_my_session('devname')
    try:
        cv_model_name = devname+"/cv.joblib"
        le_model_name = devname+"/le.joblib"
        sk_model_name = devname+"/sk.joblib"
        lr_model_name = devname+"/lr.joblib"
        class Data: pass
        sentiment = Data()
        sentiment.train_data, sentiment.train_labels = transfer_stream(request.FILES["up_dev_file"])
        counter = len(sentiment.train_labels)
        print("transfered!")
        dev_stat_ = dev_statistics(sentiment, cv_model_name, le_model_name, sk_model_name, lr_model_name)
        # print(dev_stat_)
        context = {
            'PresicionScore':dev_stat_['PresicionScore'],
            'F1Score':dev_stat_['F1Score'],
            'total_sample' : counter,
            'devname': devname,
            "train_acc" : dev_stat_['AccuracyScore'],
            'mode' : mode,
            'label': None,
            'data_name':get_dataname(devname),
            'dataset_name': get_datasets(mode == "eval_mode" or mode == "pred_mode"),
        }
        return HttpResponse(template.render(context, request))
    except Exception as error:
        print(error)
        context = {
            'total_sample' : None,
            'mode' : mode,
            'label': None,
            'data_name':get_dataname(devname),
            'dataset_name': get_datasets(mode == "eval_mode" or mode == "pred_mode"),
        }
        return HttpResponse(template.render(context, request))


def simple_upload(request):
    template = loader.get_template('index.html')
    mode = load_my_session('mode')
    devname = load_my_session('devname')
    companies = get_company()
    try:
        new_devname = "data/"+request.POST.get('new_devname')
        if new_devname == None or new_devname == "data/":
            new_devname = "data/new_model_"+str(len(os.listdir("data")))
        new_devname = new_devname + "_untrained"
        os.makedirs(new_devname)
        add_save_my_session('devname',new_devname)
        devname = load_my_session('devname')
        filename = new_devname+"/labeled_collection.tsv"
        try:
            upload = request.FILES["labeled_tsv_file"]
        except:
            shutil.rmtree(devname)
            devname = None
            raise Exception('Invalide File')
        counter, classes_ = transfer_labeled_tsvfile(filename, upload)
        if counter is None or counter < 10:
            shutil.rmtree(devname)
            devname = None
            raise Exception('Invalide File')
        trigram_model_name = devname+"/trigram.file"
        corpus = read_tsv_list(filename)
        mymodel = MyModel(corpus)
        mymodel.fit_corpus(corpus)
        sampler = MySampler(mymodel)
        with open(trigram_model_name, "a+") as f:
            for i in range(50):
                random_sentence = " ".join(sampler.sample_sentence(['START', 'START'], 10))
                f.write(random_sentence+"\n")
        context = {
            'companies':companies,
            'classes_':classes_,
            'total_sample' : count_labeled_examples(filename)[0],
            'mode' : 'train_mode',
            'label': None,
            'data_name':get_dataname(devname),
            'dataset_name': get_datasets(mode == "eval_mode" or mode == "pred_mode"),
        }
        return HttpResponse(template.render(context, request))
    except Exception as error:
        print(error)
        context = {
            'companies':companies,
            'total_sample' : None,
            'mode' : 'train_mode',
            'label': None,
            'data_name':get_dataname(devname),
            'dataset_name': get_datasets(mode == "eval_mode" or mode == "pred_mode"),
        }
        return HttpResponse(template.render(context, request))

def eval_mode(request):
    try:
        template = loader.get_template('index.html')
        add_save_my_session('mode', 'eval_mode')
        mode = load_my_session('mode')
        devname = load_my_session('devname')
        le_model_name = devname+"/le.joblib"
        le = load(le_model_name)
        classes_ = le.classes_
    except:
        classes_ = []
    context = {
        'classes_': classes_,
        'devname': None if devname is None else devname[5:],
        'total_sample' : None,
        'mode' : mode,
        'label': None,
        'data_name':get_dataname(devname),
        'dataset_name': get_datasets(mode == "eval_mode" or mode == "pred_mode"),
    }
    print("eval_mode..")
    return HttpResponse(template.render(context, request))

def add_mode(request):
    template = loader.get_template('index.html')
    add_save_my_session('mode', 'add_mode')
    mode = load_my_session('mode')
    devname = load_my_session('devname')
    total_sample, classes_ = 0, None
    random_sentence_list = []
    try:
        trigram_model_name = devname+"/trigram.file"
        with open(trigram_model_name, "r") as f:
            for line in f:
                random_sentence_list.append(line.strip())
        total_sample, classes_ = count_labeled_examples(devname+"/labeled_collection.tsv")
    except Exception as e:
        print(e)
        pass
    context = {
        'sentence_list':random_sentence_list,
        'devname': None if devname is None else devname[5:],
        'total_sample' : total_sample,
        'classes_' : classes_,
        'mode' : mode,
        'label': None,
        'data_name':get_dataname(devname),
        'dataset_name': get_datasets(mode == "eval_mode" or mode == "pred_mode"),
    }
    print("add_mode..")
    return HttpResponse(template.render(context, request))



def train_mode(request):
    template = loader.get_template('index.html')
    add_save_my_session('mode', 'train_mode')
    mode = load_my_session('mode')
    devname = load_my_session('devname')
    random_sentence_list = []
    companies = get_company()
    total_sample, classes_ = 0,None
    try:
        total_sample, classes_ = count_labeled_examples(devname+"/labeled_collection.tsv")
        trigram_model_name = devname+"/trigram.file"
        with open(trigram_model_name, "r") as f:
            for line in f:
                random_sentence_list.append(line.strip())
    except Exception as e:
        print(e)
    context = {
        'companies': companies,
        'sentence_list':random_sentence_list,
        'devname': None if devname is None else devname[5:],
        'total_sample' : total_sample,
        'classes_' : classes_,
        'mode' : mode,
        'label': None,
        'data_name':get_dataname(devname),
        'dataset_name': get_datasets(mode == "eval_mode" or mode == "pred_mode"),
    }
    print("train_mode..")
    return HttpResponse(template.render(context, request))

def index(request):
    template = loader.get_template('index.html')
    add_save_my_session('mode', 'pred_mode')
    mode = load_my_session('mode')
    devname = load_my_session('devname')
    try:
        random_sentence_list = []
        trigram_model_name = devname+"/trigram.file"
        with open(trigram_model_name, "r") as f:
            for line in f:
                random_sentence_list.append(line.strip())
        le_model_name = devname+"/le.joblib"
        le = load(le_model_name)
        if request.method == "GET":
            context = {
                'classes_': le.classes_,
                'sentence_list': random_sentence_list,
                'devname': None if devname is None else devname[5:],
                'mode' : mode,
                'data_name':get_dataname(devname),
                'dataset_name': get_datasets(mode == "eval_mode" or mode == "pred_mode"),
                'label': None,
            }
            return HttpResponse(template.render(context, request))

        elif request.method == 'POST':
            sentence = request.POST.get('sentence')
            template = loader.get_template('index.html')
            context = {
                'sentence_list': random_sentence_list,
                'label': sentence,
                'data_name':get_dataname(devname),
                'dataset_name': get_datasets(mode == "eval_mode" or mode == "pred_mode"),
            }
            return HttpResponse(template.render(context, request))
    except:
        context = {
            'sentence_list': [],
            'label': None,
            'data_name': None,
            'dataset_name': get_datasets(mode == "eval_mode" or mode == "pred_mode"),
        }
        return HttpResponse(template.render(context, request))


# Create your views here.
def results(request):
    try:
        sentence = request.POST.get('sentence')
        template = loader.get_template('index.html')
        devname = load_my_session('devname')
        mode = load_my_session('mode')
        filename = devname+"/labeled_collection.tsv"
        cv_model_name = devname+"/cv.joblib"
        le_model_name = devname+"/le.joblib"
        sk_model_name = devname+"/sk.joblib"
        lr_model_name = devname+"/lr.joblib"
        label, score, classes_ = predict(sentence, cv_model_name, le_model_name, sk_model_name, lr_model_name)
        explainK,explainV =  explain_grams_list(sentence, cv_model_name, le_model_name, sk_model_name, lr_model_name, False)
        topA_val,topA_name,topB_val,topB_name = topKsignificance(20, cv_model_name,sk_model_name,lr_model_name,le_model_name)
        context = {
            'explainK':explainK,
            'explainV':explainV,
            'topA_val': topA_val if label == classes_[0] else [],
            'topA_name': topA_name if label == classes_[0] else [],
            'topB_val': topB_val if label == classes_[1] else [],
            'topB_name': topB_name if label == classes_[1] else [],
            "class_a": [classes_[0]],
            "class_b": [classes_[1]],
            "devname": None if devname is None else devname[5:],
            "sentence": sentence,
            "label": [label],
            'mode' : None,
            "sent_conf": float(score),
            'data_name':get_dataname(devname),
            'dataset_name': get_datasets(mode == "eval_mode" or mode == "pred_mode"),
        }
        add_save_my_session('sentence',sentence)
        return HttpResponse(template.render(context, request))
    except:
        return index(request)
    # <ul>
    # {% for key, value in choices.items %}
    #   <li>{{key}} - {{value}}</li>
    #  {% endfor %}
    # </ul>

def plot(request):
    # print(request.POST.get('sentence'))
    # sentence = request.session['sentence']
    sentence = load_my_session('sentence')
    devname  = load_my_session('devname')
    filename = devname+"/labeled_collection.tsv"
    cv_model_name = devname+"/cv.joblib"
    le_model_name = devname+"/le.joblib"
    sk_model_name = devname+"/sk.joblib"
    lr_model_name = devname+"/lr.joblib"

    result = explain_grams(sentence, cv_model_name, le_model_name, sk_model_name, lr_model_name, True)
    response = JsonResponse(result)
    return response

def update(request):
    devname = load_my_session('devname')
    sentence = load_my_session('sentence')
    mode = load_my_session('mode')
    filename = devname+"/labeled_collection.tsv"
    cv_model_name = devname+"/cv.joblib"
    le_model_name = devname+"/le.joblib"
    sk_model_name = devname+"/sk.joblib"
    lr_model_name = devname+"/lr.joblib"
    dataPoints = request.POST.get("dataPoints")
    dataPoints = json.loads(dataPoints)
    grams = {}
    for data in dataPoints:
        grams[data["label"]] = data["y"]
    update_model(sentence, grams, cv_model_name, le_model_name, sk_model_name, lr_model_name)

    template = loader.get_template('index.html')
    label, score = predict(sentence, cv_model_name, le_model_name, sk_model_name, lr_model_name)
    context = {
        "sentence": sentence,
        "label": str(label),
        "mode": mode,
        "score": float(score),
        'data_name':get_dataname(devname),
        'dataset_name': get_datasets(mode == "eval_mode" or mode == "pred_mode"),
    }
    return HttpResponse(template.render(context, request))


def explain(request):
    # sentence = request.session['sentence'] #request.POST.get('sentence')
    # devname = request.session['devname']
    sentence = load_my_session('sentence')
    devname = load_my_session('devname')
    filename = devname+"/labeled_collection.tsv"
    cv_model_name = devname+"/cv.joblib"
    le_model_name = devname+"/le.joblib"
    sk_model_name = devname+"/sk.joblib"
    lr_model_name = devname+"/lr.joblib"
    result = explain_grams(sentence, cv_model_name, le_model_name, sk_model_name, lr_model_name,False)
    return JsonResponse(result)
