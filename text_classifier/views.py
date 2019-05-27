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
        try:
            os.makedirs("data")
        except OSError:
            shutil.rmtree("data")
            os.makedirs("data")
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
    label = predict(sentence, cv_model_name, sk_model_name, lr_model_name)
    context = {
        "sentence": sentence,
        "label": label
    }
    return HttpResponse(template.render(context, request))
