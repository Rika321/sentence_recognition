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

filename = ''
cv_model_name = ""
sk_model_name = ""
lr_model_name = ""
devname = ""

# def predict(sentence):
#     print("predicting")
#     if random.random() > 0.5:
#         return "negative"
#     else:
#         return "positive"
# Create your views here.

def apply_model(request):
    template = loader.get_template('index.html')

    devname    = request.POST.get('sel_data')
    request.session['devname'] = "data/"+devname
    print(request.session['devname'])

    context = {
        'devname': devname,
        'total_sample' : count_labeled_examples(devname),
        'label': None,
        'mode' : 'eval_mode',
        'dataset_name': os.listdir("data"),
    }
    return HttpResponse(template.render(context, request))




def simple_train(request):
    template = loader.get_template('index.html')
    if request.method == 'POST':
        devname = request.session['devname']
        filename = devname+"/labeled_collection.tsv"
        cv_model_name = devname+"/cv.joblib"
        sk_model_name = devname+"/sk.joblib"
        lr_model_name = devname+"/lr.joblib"

        print(".......",filename)
        sentiment = read_files(filename)
        print("\nTraining classifier")
        transform_data(sentiment,cv_model_name)
        select_feature(sentiment,sk_model_name)
        acc = train_classifier( sentiment.trainX_select, sentiment.trainy, lr_model_name)
        # os.remove(filename)
        context = {
            'devname': devname,
            "train_acc" : acc,
            'total_sample' : None,
            'mode' : 'train_mode',
            'label': None,
            'dataset_name': os.listdir("data"),
        }
        return HttpResponse(template.render(context, request))
    else:
        context = {
            'total_sample' : None,
            'mode' : 'train_mode',
            'label': None,
            'dataset_name': os.listdir("data"),
        }
        return HttpResponse(template.render(context, request))



def simple_add(request):
    template = loader.get_template('index.html')
    if request.method == 'POST' and request.POST.get('sentence') != "":
        sentence = request.POST.get('sentence')
        label    = request.POST.get('label')

        devname = request.session['devname']
        filename = devname+"/labeled_collection.tsv"

        counter = transfer_one_line(filename, sentence, label)
        context = {
            'total_sample' : count_labeled_examples(devname),
            'mode' : 'train_mode',
            'label': None,
            'dataset_name': os.listdir("data"),
        }
        return HttpResponse(template.render(context, request))

    context = {
        'total_sample' : count_labeled_examples(devname),
        'mode' : 'train_mode',
        'label': None,
        'dataset_name': os.listdir("data"),
    }
    return HttpResponse(template.render(context, request))


def simple_upload(request):
    template = loader.get_template('index.html')
    if request.method == 'POST':
        try:
            devname = "data/"+request.POST.get('devname')
            try:
                os.makedirs(devname)
            except OSError:
                print("existed file")

            request.session['devname'] = devname
            filename = devname+"/labeled_collection.tsv"
            cv_model_name = devname+"/cv.joblib"
            sk_model_name = devname+"/sk.joblib"
            lr_model_name = devname+"/lr.joblib"

            counter = transfer_labeled_tsvfile(filename, request.FILES["labeled_tsv_file"])
            print(counter)
            print(devname.split("/"))
            context = {
                'data_name': devname.split("/")[1],
                'read_sample'  : counter,
                'total_sample' : count_labeled_examples(filename),
                'mode' : 'train_mode',
                'label': None,
                'dataset_name': os.listdir("data"),
            }
            return HttpResponse(template.render(context, request))
        except Exception as error:
            print(error)

    context = {
        'total_sample' : count_labeled_examples(),
        'mode' : 'train_mode',
        'label': None,
        'dataset_name': os.listdir("data"),
    }
    return HttpResponse(template.render(context, request))



def train_mode(request):
    template = loader.get_template('index.html')
    devname = request.session['devname']
    context = {
        'devname': devname[5:],
        'total_sample' : count_labeled_examples(devname),
        'mode' : 'train_mode',
        'label': None,
        'dataset_name': os.listdir("data"),
    }
    print("train_mode..")
    return HttpResponse(template.render(context, request))

def index(request):
    devname = request.session['devname']
    if request.method == "GET":
        # try:
        #     os.makedirs("data")
        # except OSError:
        #     shutil.rmtree("data")
        #     os.makedirs("data")
            # print ("Creation of the directory %s failed" % path)
        template = loader.get_template('index.html')
        context = {
            'devname': devname[5:],
            'mode' : 'eval_mode',
            'dataset_name': os.listdir("data"),
            'label': None,
        }
        print("eval...")
        return HttpResponse(template.render(context, request))

    elif request.method == 'POST':
        sentence = request.POST.get('sentence')
        template = loader.get_template('index.html')


        context = {
            'label': sentence,
            'dataset_name': os.listdir("data"),
        }
        return HttpResponse(template.render(context, request))

# Create your views here.
def results(request):
    # if request.method == 'POST':
    sentence = request.POST.get('sentence')
    template = loader.get_template('index.html')
    devname = request.session['devname']
    filename = devname+"/labeled_collection.tsv"
    cv_model_name = devname+"/cv.joblib"
    sk_model_name = devname+"/sk.joblib"
    lr_model_name = devname+"/lr.joblib"
    label, score = predict(sentence, cv_model_name, sk_model_name, lr_model_name)
    context = {
        "devname": devname[5:],
        "sentence": sentence,
        "label": str(label),
        "score": float(score),
        'dataset_name': os.listdir("data"),
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
    sentence = request.session['sentence']
    devname = request.session['devname']
    filename = devname+"/labeled_collection.tsv"
    cv_model_name = devname+"/cv.joblib"
    sk_model_name = devname+"/sk.joblib"
    lr_model_name = devname+"/lr.joblib"

    result = explain_grams(sentence, cv_model_name, sk_model_name, lr_model_name, True)
    # result = {'food':[-0.8,1],'is':0.1,'very':-0.5,\
    #  'good':3,'what':1,'bad':-2}
    print(result)
    return JsonResponse(result)

def update(request):
    devname = request.session['devname']
    filename = devname+"/labeled_collection.tsv"
    cv_model_name = devname+"/cv.joblib"
    sk_model_name = devname+"/sk.joblib"
    lr_model_name = devname+"/lr.joblib"
    dataPoints = request.POST.get("dataPoints")
    dataPoints = json.loads(dataPoints)
    grams = [[data["label"],data["y"]] for data in dataPoints]
    update_model(grams, cv_model_name, sk_model_name, lr_model_name)
    # [{"label":"food","y":-0.9696667228377398,"color":"rgb(255,127,0)","x":0},{"label":"is","y":0.42468344845046,"color":"rgb(204,255,0)","x":1},{"label":"good","y":1.786179814172434,"color":"rgb(30,255,0)","x":2},{"label":"food is","y":-0.44760840323097706,"color":"rgb(255,193,0)","x":3},{"label":"is good","y":0.6428565081329942,"color":"rgb(173,255,0)","x":4}]
    # for dataPoint in dataPoints:
    # result = {'food':-0.8,'is':0.1,'very':-0.5,\
    #  'good':3,'what':1,'bad':-2}

    template = loader.get_template('index.html')
    label, score = predict(sentence, cv_model_name, sk_model_name, lr_model_name)
    context = {
        "sentence": sentence,
        "label": str(label),
        "score": float(score),
        'dataset_name': os.listdir("data"),
    }
    return HttpResponse(template.render(context, request))


def explain(request):
    sentence = request.session['sentence'] #request.POST.get('sentence')
    devname = request.session['devname']
    filename = devname+"/labeled_collection.tsv"
    cv_model_name = devname+"/cv.joblib"
    sk_model_name = devname+"/sk.joblib"
    lr_model_name = devname+"/lr.joblib"
    result = explain_grams(sentence, cv_model_name, sk_model_name, lr_model_name,False)
    return JsonResponse(result)
