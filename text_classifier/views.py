from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

import random


def predict(sentence):
    print("predicting")
    if random.random() > 0.5:
        return "negative"
    else:
        return "positive"
# Create your views here.
def index(request):
    if request.method == "GET":
        template = loader.get_template('index.html')
        context = {
            "label": None
        }
        return HttpResponse(template.render(context, request))

    elif request.method == 'POST':
        sentence = request.POST.get('sentence')
        template = loader.get_template('index.html')

        context = {
            "label": sentence
            # 'current_name': latest_question_lisst,
        }
        return HttpResponse(template.render(context, request))

# Create your views here.
def results(request):
    # if request.method == 'POST':
    sentence = request.POST.get('sentence')
    template = loader.get_template('index.html')
    context = {
        "sentence": sentence,
        "label": predict(sentence)
    }
    return HttpResponse(template.render(context, request))
