import os
import sys
import argparse
from joblib import dump, load
import numpy as np


import requests

from django.shortcuts import render
import operator

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, 'templates\models')

from . import models

def getFINDRISK(d):
    score = 0
    
    if d['age'] >= 45 and d['age'] <= 54:
        score += 2
    elif d['age'] >= 55 and d['age'] <= 64:
        score += 3
    elif d['age'] >= 65:
        score +=4

    if d['BMI'] >= 25 and d['BMI'] <= 30:
        score += 1
    elif d['BMI'] >= 30:
        score +=3

    if d['waist'] == "1":
        score += 4
    elif d['waist'] == "2":
        score +=4

    if d['exercise'] != "5":
        score +=2

    if d['fvc'] != "5":
        score +=1

    if d['preparats'] == "1":
        score +=2

    if d['high_glucose'] == "1":
        score +=5

    if d['diabete_family'] == "far":
        score +=3
    elif d['diabete_family'] == "relatives":
        score +=5

    answer = ""

    if score < 7:
        answer = "У Вас низкий шанс развития сахарного диабета. Примерно у 1 человека из 100 будет диабет."
    elif score >= 7 and score <= 11:
        answer = "У Вас немного повышен шанс развития сахарного диабета. Примерно у 1 человека из 25 будет диабет."
    elif score >= 12 and score <= 14:
        answer = "У Вас умеренный шанс развития сахарного диабета. Примерно у 1 человека из 6 будет диабет."
    elif score >= 15 and score <= 20:
         answer = "У Вас высокий шанс развития сахарного диабета. Примерно у 1 человека из 3 будет диабет."
    elif score >= 20:
         answer = "У Вас очень высокий шанс развития сахарного диабета. Примерно у 1 человека из 2 будет диабет."
   
    return answer

def MakeDataForModel(d):
    
    if d['smoking'] == 3:
        smoking = 0
    else:
        smoking = 1

    exercise = int(d['exercise'])
    FVC = int(d['FVC'])

    data = [d['age'], d['gender'], d['education'], smoking, d['HBP'], d['HD'], d['smoking'], exercise, FVC, d['DK']]


    return data

def getMODEL(d):

    MODEL_FILE = MODELS_DIR + '\model.joblib'

    clf = load(MODEL_FILE)
    data = np.array(d)
    data.reshape(1, -1)
    out = clf.predict([d])
    
    if out == 1:
        asnwer = "Модель показала результат, что с очень большой вероятностью вы уже имеете у себя сахарный диабет. Настоятельно рекомендуется посетить врача для получения точного диагноза."
    else:
        asnwer = "Модель показала результат, что вы не больны сахарным диабетом на данный момент."
 
    return asnwer

# Create your views here.
def index(request):
    return render(request, 'diabet/index.html')

def about(request):
   return render(request, 'diabet/about.html')

def poll(request):
    return render(request, 'diabet/poll.html')

def result(request):

 if request.method == 'POST':
    
    if request.POST.get('suggestions') != "":
        models.Comments.objects.create(text=request.POST.get('suggestions'))

    age = int(request.POST.get('age'))
    DK = int(request.POST.get('DK'))
    gender = int(request.POST.get('gender'))
    race = int(request.POST.get('race'))
    education = int(request.POST.get('education'))
    smoking = int(request.POST.get('smoking'))
    heart_diseases = int(request.POST.get('heart_diseases'))
    high_blood_presure = int(request.POST.get('high_blood_presure'))

    height = float(request.POST.get('height'))
    weight = float(request.POST.get('weight'))
    BMI = weight / (height * height)

    waist = request.POST.get('waist')
    exercise = request.POST.get('exercise')
    fvc = request.POST.get('fvc')
    preparats = request.POST.get('preparats')
    high_glucose = request.POST.get('high_glucose')
    diabete_family = request.POST.get('diabete_family')

    FINDRISK_DATA = {
            'age':age, 'BMI':BMI, 'waist':waist , 'exercise':exercise, 'fvc':fvc,
            'preparats':preparats, 'high_glucose':high_glucose, 'diabete_family':diabete_family,
    }

    NotClearMODELDATA = {
            'age':age, 'gender':gender, 'race':race , 'education':education, 'smoking':smoking,
            'HBP':high_blood_presure, 'HD':heart_diseases, 'exercise':exercise,
            'FVC':fvc, 'DK':DK,
    }

    ModelData = MakeDataForModel(NotClearMODELDATA)
    
    MODEL_SCORE = getMODEL(ModelData)
    FINDRISK_SCORE = getFINDRISK(FINDRISK_DATA) 

    scores = {
        'FINDRISK_SCORE' : FINDRISK_SCORE, 'MODEL_SCORE': MODEL_SCORE,
    }
   
    return render(request, 'diabet/results.html', scores)


