import os
import sys
from django.shortcuts import render
from rest_framework.views import APIView
from django.http import HttpResponse
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status
from itertools import chain
from django.core import serializers
from firebase_admin import firestore
import json
sys.path.append("..")
from mysite.users.models import user_info, exam_info
from mysite.course_data.models import questionSagar, Classcast_test_submission, student_topic_interaction, chapter, classcast_question, question, exams_package, exams, test_sections, chapter_updated
from datetime import datetime 
from django.views.decorators.csrf import csrf_exempt
import google.oauth2.id_token
import google.auth.transport.requests
import random
import uuid

HTTP_REQUEST = google.auth.transport.requests.Request()

def hello(request):
    text = """<h1>welcome to my app !</h1>"""
    return HttpResponse(text)


@csrf_exempt 
def createChallenge(request):

    #id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
    #claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
    #if not claims:
    #    return HttpResponse('Unauthorized')
    #username = claims['firebase']['identities']['phone'][0][3:13]
    username = "1111111133"

    student=user_info.objects.get(username=username)
    
    if(request.method == "GET"):
        return JsonResponse({'status': 'False', 'message': 'Get request'})
    user_json_data=json.loads(request.body)

    standard = student.standard
    goal = exam_info.objects.get(exam_id=standard)

    challenge_id = str(uuid.uuid4())

    #return HttpResponse(user_infoList.firstname)
    #user_json_data[10]['challenge_to'] = "abcd"
    user_json_data['challenge_by'] = username
    user_json_data['challenge_by_name'] = student.firstname + ' '+ student.lastname
    user_json_data['challenge_id'] = challenge_id
    user_json_data['challenge_created_at'] = datetime.today().strftime("%Y-%m-%d %H:%M:%S")

    package = user_json_data['exams_package']
    exam_name = user_json_data['exam_name']
    chapter = user_json_data['chapter']
    duration = user_json_data['duration']

    if(duration == 10):
        no_of_questions_per_section = 10
    else:
        no_of_questions_per_section = 20

    db = firestore.Client()
    doc_ref = db.collection(u'challenge').document(challenge_id)

    doc_ref.set(user_json_data)


    index = random.randint(1,100)

    challenge_data = []
    db = firestore.Client()

    quesList=[]
      
    doc_ref = db.collection(u'new_question_database').document(u'exams').collection(goal.exam_name).document(exam_name).collection(package).where(u'section', u'==', chapter).where(u'index', u'>=', index)
    doc = doc_ref.limit(no_of_questions_per_section).get()
      
    for el in doc:
        quesList.append(el.to_dict())
      
    
    if(len(quesList) < no_of_questions_per_section):
        remaining_no_of_questions_per_section = no_of_questions_per_section - len(quesList)
        doc_ref = db.collection(u'new_question_database').document(u'exams').collection(goal.exam_name).document(exam_name).collection(package).where(u'section', u'==', chapter).where(u'index', u'>=', 0)
        doc = doc_ref.limit(remaining_no_of_questions_per_section).get()
        for el in doc:
            quesList.append(el.to_dict())


    challenge_data.append(
        {
          "section": chapter,
          "section_name": chapter,
          "data": quesList
        }
      )

    data = {
        "challenge_data": challenge_data,
        "sender_answers": [],
        "receiver_answers": []
    }

    doc_ref = db.collection(u'challenge_questions').document(challenge_id)
    doc_ref.set(data)
    
    return JsonResponse({'challenge_id': challenge_id}, status=200)











    return HttpResponse(challenge_id)
    if(standard == 'all'):
        qs = question.objects.filter(chapter__iexact=user_json_data['chapter'].strip()).order_by('?').values_list('xblock_id', flat=True)
    else:
        qs = question.objects.filter(chapter__iexact=user_json_data['chapter'], standard = standard).order_by('?').values_list('xblock_id', flat=True)

    if(len(qs) >= 15):
        qs1 = qs[0:15]
    else:
        qs1 = qs[0:len(qs)-1]

    a = {"questions": qs1}

    thisdict = {
        "challenge_id": challenge_id,
        "questions": qs1,
        "sender_answers": [],
        "receiver_answers": []
      }

    doc_ref = db.collection(u'challenge_questions').document(challenge_id)
    doc_ref.set(thisdict)
    #return HttpResponse(challenge_id)
    return JsonResponse({'challenge_id': challenge_id}, status=200)
