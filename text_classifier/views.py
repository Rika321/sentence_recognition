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
from django import forms
import os
import shutil
from django.http import JsonResponse
import json

filename = 'data/labeled_collection.tsv'
cv_model_name = "data/cv.joblib"
sk_model_name = "data/sk.joblib"
lr_model_name = "data/lr.joblib"

# def predict(sentence):
#     print("predicting")
#     if random.random() > 0.5:
#         return "negative"
#     else:
#         return "positive"
# Create your views here.


def simple_train(request):
    template = loader.get_template('index.html')
    if request.method == 'POST':
        sentiment = read_files(filename)
        print("\nTraining classifier")
        transform_data(sentiment,cv_model_name)
        select_feature(sentiment,sk_model_name)
        acc = train_classifier( sentiment.trainX_select, sentiment.trainy, lr_model_name)
        os.remove(filename)
        context = {
            "train_acc" : acc,
            'total_sample' : None,
            'mode' : 'train_mode',
            'label': None,
        }
        return HttpResponse(template.render(context, request))
    else:
        context = {
            'total_sample' : None,
            'mode' : 'train_mode',
            'label': None,
        }
        return HttpResponse(template.render(context, request))



def simple_add(request):
    template = loader.get_template('index.html')
    if request.method == 'POST' and request.POST.get('sentence') != "":
        sentence = request.POST.get('sentence')
        label    = request.POST.get('label')
        # print(sentence)
        # print(label)
        counter = transfer_one_line(sentence, label)
        context = {
            'total_sample' : count_labeled_examples(),
            'mode' : 'train_mode',
            'label': None,
        }
        return HttpResponse(template.render(context, request))

    context = {
        'total_sample' : count_labeled_examples(),
        'mode' : 'train_mode',
        'label': None,
    }
    return HttpResponse(template.render(context, request))


def simple_upload(request):
    template = loader.get_template('index.html')
    if request.method == 'POST':
        try:
            counter = transfer_labeled_tsvfile(request.FILES["labeled_tsv_file"])
            context = {
                'read_sample'  : counter,
                'total_sample' : count_labeled_examples(),
                'mode' : 'train_mode',
                'label': None,
            }
            return HttpResponse(template.render(context, request))
        except Exception as error:
            print(error)

    context = {
        'total_sample' : count_labeled_examples(),
        'mode' : 'train_mode',
        'label': None,
    }
    return HttpResponse(template.render(context, request))



def train_mode(request):
    template = loader.get_template('index.html')
    context = {
        'total_sample' : count_labeled_examples(),
        'mode' : 'train_mode',
        'label': None,
    }
    print("train_mode..")
    return HttpResponse(template.render(context, request))

def index(request):
    if request.method == "GET":
        # try:
        #     os.makedirs("data")
        # except OSError:
        #     shutil.rmtree("data")
        #     os.makedirs("data")
            # print ("Creation of the directory %s failed" % path)


        template = loader.get_template('index.html')
        context = {
            'mode' : 'eval_mode',
            'label': None,
        }
        print("eval...")
        return HttpResponse(template.render(context, request))

    elif request.method == 'POST':
        sentence = request.POST.get('sentence')
        template = loader.get_template('index.html')

        context = {
            'label': sentence
            # 'current_name': latest_question_lisst,
        }
        return HttpResponse(template.render(context, request))

# Create your views here.
def results(request):
    # if request.method == 'POST':
    sentence = request.POST.get('sentence')
    template = loader.get_template('index.html')
    label, score = predict(sentence, cv_model_name, sk_model_name, lr_model_name)
    context = {
        "sentence": sentence,
        "label": str(label),
        "score": float(score),
    }
    request.session['sentence'] = sentence
    return HttpResponse(template.render(context, request))

    # <ul>
    # {% for key, value in choices.items %}
    #   <li>{{key}} - {{value}}</li>
    #  {% endfor %}
    # </ul>

def plot(request):
    # print(request.POST.get('sentence'))
    sentence = request.session['sentence'] #request.POST.get('sentence')
    result = explain_grams(sentence, cv_model_name, sk_model_name, lr_model_name, True)
    # result = {'food':[-0.8,1],'is':0.1,'very':-0.5,\
    #  'good':3,'what':1,'bad':-2}
    print(result)
    return JsonResponse(result)

def update(request):
    dataPoints = request.POST.get("dataPoints")
    dataPoints = json.loads(dataPoints)
    grams = [[data["label"],data["y"]] for data in dataPoints]
    update_model(grams, cv_model_name, sk_model_name, lr_model_name)
    # [{"label":"food","y":-0.9696667228377398,"color":"rgb(255,127,0)","x":0},{"label":"is","y":0.42468344845046,"color":"rgb(204,255,0)","x":1},{"label":"good","y":1.786179814172434,"color":"rgb(30,255,0)","x":2},{"label":"food is","y":-0.44760840323097706,"color":"rgb(255,193,0)","x":3},{"label":"is good","y":0.6428565081329942,"color":"rgb(173,255,0)","x":4}]
    # for dataPoint in dataPoints:

    result = {'food':-0.8,'is':0.1,'very':-0.5,\
     'good':3,'what':1,'bad':-2}
    return JsonResponse(result)


def explain(request):
    sentence = request.session['sentence'] #request.POST.get('sentence')
    # print("sentence is",sentence)
    result = explain_grams(sentence, cv_model_name, sk_model_name, lr_model_name,False)
    # result = {'food':-0.8,'is':0.1,'very':-0.5,\
    #  'good':3,'what':1,'bad':-2}
    return JsonResponse(result)
