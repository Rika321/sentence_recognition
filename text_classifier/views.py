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
import json

filename = ''
cv_model_name = ""
sk_model_name = ""
lr_model_name = ""
devname = ""
mode = ""



def apply_model(request):
    template = loader.get_template('index.html')
    devname    = "data/"+request.POST.get('sel_data')
    add_save_my_session('devname',devname)
    mode = load_my_session('mode')
    # request.session['devname'] = "data/"+devname
    context = {
        'devname': None if devname is None else devname[5:],
        'total_sample' : count_labeled_examples(devname),
        'label': None,
        'mode' : mode,
        'data_name': None if devname is None else devname.split("/")[1],
        'dataset_name': [""]+os.listdir("data"),
    }
    return HttpResponse(template.render(context, request))

# def helper(dev):
#     ddd


def simple_train(request):
    template = loader.get_template('index.html')
    mode = load_my_session('mode')
    devname = load_my_session('devname') #request.session['devname']
    filename = devname+"/labeled_collection.tsv"
    cv_model_name = devname+"/cv.joblib"
    sk_model_name = devname+"/sk.joblib"
    lr_model_name = devname+"/lr.joblib"
    sentiment = read_files(filename)
    print("\nTraining classifier")
    transform_data(sentiment,cv_model_name)
    select_feature(sentiment,sk_model_name)
    acc = train_classifier( sentiment.trainX_select, sentiment.trainy, lr_model_name)
    dev_stat_ = dev_statistics(filename, cv_model_name, sk_model_name, lr_model_name)
    print(dev_stat_)
    context = {
        'PresicionScore':dev_stat_['PresicionScore'],
        'F1Score':dev_stat_['F1Score'],
        'total_sample' : count_labeled_examples(filename),
        'devname': devname,
        "train_acc" : acc,
        'mode' : mode,
        'label': None,
        'data_name': None if devname is None else devname.split("/")[1],
        'dataset_name': [""]+os.listdir("data"),
    }
    return HttpResponse(template.render(context, request))




def simple_add(request):
    template = loader.get_template('index.html')
    mode = load_my_session('mode')
    if request.method == 'POST' and request.POST.get('sentence') != "":
        sentence = request.POST.get('sentence')
        label    = request.POST.get('label')

        devname = load_my_session('devname')
        filename = devname+"/labeled_collection.tsv"

        counter = transfer_one_line(filename, sentence, label)
        context = {
            'total_sample' : count_labeled_examples(devname),
            'mode' : mode,
            'label': None,
            'data_name': None if devname is None else devname.split("/")[1],
            'dataset_name': [""]+os.listdir("data"),
        }
        return HttpResponse(template.render(context, request))

    context = {
        'total_sample' : count_labeled_examples(devname),
        'mode' : mode,
        'label': None,
        'data_name': None if devname is None else devname.split("/")[1],
        'dataset_name': [""]+os.listdir("data"),
    }
    return HttpResponse(template.render(context, request))


def simple_eval(request):
    template = loader.get_template('index.html')
    mode = load_my_session('mode')
    devname = load_my_session('devname')
    try:
        cv_model_name = devname+"/cv.joblib"
        sk_model_name = devname+"/sk.joblib"
        lr_model_name = devname+"/lr.joblib"
        # print("test")
        class Data: pass
        sentiment = Data()
        sentiment.train_data, sentiment.train_labels = transfer_stream(request.FILES["up_dev_file"])
        print("transfered!")
        dev_stat_ = dev_statistics_sentiment(sentiment, cv_model_name, sk_model_name, lr_model_name)
        print(dev_stat_)
        context = {
            'PresicionScore':dev_stat_['PresicionScore'],
            'F1Score':dev_stat_['F1Score'],
            'total_sample' : count_labeled_examples(filename),
            'devname': devname,
            "train_acc" : dev_stat_['AccuracyScore'],
            'mode' : mode,
            'label': None,
            'data_name': None if devname is None else devname.split("/")[1],
            'dataset_name': [""]+os.listdir("data"),
        }
        return HttpResponse(template.render(context, request))
    except Exception as error:
        print(error)
        context = {
            'total_sample' : None,
            'mode' : mode,
            'label': None,
            'data_name': None if devname is None else devname.split("/")[1],
            'dataset_name': [""]+os.listdir("data"),
        }
        return HttpResponse(template.render(context, request))




def simple_upload(request):
    template = loader.get_template('index.html')
    mode = load_my_session('mode')
    try:
        new_devname = "data/"+request.POST.get('new_devname')
        try:
            os.makedirs(new_devname)
        except OSError:
            print("existed file")
        add_save_my_session('devname',new_devname)
        devname = load_my_session('devname')
        filename = new_devname+"/labeled_collection.tsv"
        counter = transfer_labeled_tsvfile(filename, request.FILES["labeled_tsv_file"])
        context = {
            'read_sample'  : counter,
            'total_sample' : count_labeled_examples(filename),
            'mode' : 'train_mode',
            'label': None,
            'data_name': None if devname is None else devname.split("/")[1],
            'dataset_name': [""]+os.listdir("data"),
        }
        return HttpResponse(template.render(context, request))
    except Exception as error:
        print(error)
        context = {
            'total_sample' : count_labeled_examples(),
            'mode' : 'train_mode',
            'label': None,
            'data_name': None if devname is None else devname.split("/")[1],
            'dataset_name': [""]+os.listdir("data"),
        }
        return HttpResponse(template.render(context, request))

def eval_mode(request):
    template = loader.get_template('index.html')
    add_save_my_session('mode', 'eval_mode')
    mode = load_my_session('mode')
    devname = load_my_session('devname')
    context = {
        'devname': None if devname is None else devname[5:],
        'total_sample' : count_labeled_examples(devname),
        'mode' : mode,
        'label': None,
        'data_name': None if devname is None else devname.split("/")[1],
        'dataset_name': [""]+os.listdir("data"),
    }
    print("eval_mode..")
    return HttpResponse(template.render(context, request))



def train_mode(request):
    template = loader.get_template('index.html')
    add_save_my_session('mode', 'train_mode')
    mode = load_my_session('mode')
    devname = load_my_session('devname')
    context = {
        'devname': None if devname is None else devname[5:],
        'total_sample' : count_labeled_examples(devname),
        'mode' : mode,
        'label': None,
        'data_name': None if devname is None else devname.split("/")[1],
        'dataset_name': [""]+os.listdir("data"),
    }
    print("train_mode..")
    return HttpResponse(template.render(context, request))

def index(request):
    add_save_my_session('mode', 'pred_mode')
    devname = load_my_session('devname')
    mode = load_my_session('mode')
    if request.method == "GET":
        # try:
        #     os.makedirs("data")
        # except OSError:
        #     shutil.rmtree("data")
        #     os.makedirs("data")
            # print ("Creation of the directory %s failed" % path)
        template = loader.get_template('index.html')
        context = {
            'devname': None if devname is None else devname[5:],
            'mode' : mode,
            'data_name': None if devname is None else devname.split("/")[1],
            'dataset_name': [""]+os.listdir("data"),
            'label': None,
        }
        return HttpResponse(template.render(context, request))

    elif request.method == 'POST':
        sentence = request.POST.get('sentence')
        template = loader.get_template('index.html')
        context = {
            'label': sentence,
            'data_name': None if devname is None else devname.split("/")[1],
            'dataset_name': [""]+os.listdir("data"),
        }
        return HttpResponse(template.render(context, request))

# Create your views here.
def results(request):
    # if request.method == 'POST':
    sentence = request.POST.get('sentence')
    template = loader.get_template('index.html')
    devname = load_my_session('devname')
    mode = load_my_session('mode')
    filename = devname+"/labeled_collection.tsv"
    cv_model_name = devname+"/cv.joblib"
    sk_model_name = devname+"/sk.joblib"
    lr_model_name = devname+"/lr.joblib"
    label, score = predict(sentence, cv_model_name, sk_model_name, lr_model_name)
    context = {
        "devname": None if devname is None else devname[5:],
        "sentence": sentence,
        "label": str(label),
        'mode' : None,
        "sent_conf": float(score),
        'data_name': None if devname is None else devname.split("/")[1],
        'dataset_name': [""]+os.listdir("data"),
    }
    add_save_my_session('sentence',sentence)
    return HttpResponse(template.render(context, request))

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
    sk_model_name = devname+"/sk.joblib"
    lr_model_name = devname+"/lr.joblib"

    result = explain_grams(sentence, cv_model_name, sk_model_name, lr_model_name, True)
    response = JsonResponse(result)
    return response

def update(request):
    devname = load_my_session('devname')
    sentence = load_my_session('sentence')
    mode = load_my_session('mode')
    filename = devname+"/labeled_collection.tsv"
    cv_model_name = devname+"/cv.joblib"
    sk_model_name = devname+"/sk.joblib"
    lr_model_name = devname+"/lr.joblib"
    dataPoints = request.POST.get("dataPoints")
    dataPoints = json.loads(dataPoints)
    grams = {}
    for data in dataPoints:
        grams[data["label"]] = data["y"]
    update_model(sentence, grams, cv_model_name, sk_model_name, lr_model_name)

    template = loader.get_template('index.html')
    label, score = predict(sentence, cv_model_name, sk_model_name, lr_model_name)
    context = {
        "sentence": sentence,
        "label": str(label),
        "mode": mode,
        "score": float(score),
        'data_name': None if devname is None else devname.split("/")[1],
        'dataset_name': [""]+os.listdir("data"),
    }
    return HttpResponse(template.render(context, request))


def explain(request):
    # sentence = request.session['sentence'] #request.POST.get('sentence')
    # devname = request.session['devname']
    sentence = load_my_session('sentence')
    devname = load_my_session('devname')
    filename = devname+"/labeled_collection.tsv"
    cv_model_name = devname+"/cv.joblib"
    sk_model_name = devname+"/sk.joblib"
    lr_model_name = devname+"/lr.joblib"
    result = explain_grams(sentence, cv_model_name, sk_model_name, lr_model_name,False)
    return JsonResponse(result)
