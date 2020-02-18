import os
import sys
from django.shortcuts import render
from rest_framework.views import APIView
from django.http import HttpResponse
from django.http import JsonResponse
from rest_framework.response import Response
from datetime import datetime 
from rest_framework import status
from itertools import chain
from django.core import serializers
from firebase_admin import firestore
#from google.cloud import firestore
#from google.cloud.firestore_v1beta1 import ArrayRemove, ArrayUnion
import json
sys.path.append("..")
from mysite.users.models import user_info
from mysite.course_data.models import questionSagar, Classcast_test_submission, student_topic_interaction, chapter, classcast_question, question
from django.views.decorators.csrf import csrf_exempt
import google.oauth2.id_token
import google.auth.transport.requests
import uuid


HTTP_REQUEST = google.auth.transport.requests.Request()

def hello(request):
  text = """<h1>welcome to my app !</h1>"""
  return HttpResponse(text)

@csrf_exempt
def phonenumber(request):
  id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
  claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
  if not claims:
    return HttpResponse('Unauthorized')

  if(request.method == "GET"):
    return JsonResponse({'status': 'False', 'message': 'Get request'})
  user_json_data=json.loads(request.body)
  phonenumberList = user_json_data['number'];

  user_infoList = user_info.objects.filter(phone_number__in = phonenumberList).values_list('firstname','lastname','phone_number', flat=False)
  return JsonResponse(list(user_infoList), safe=False)
  #return HttpResponse(list(user_infoList))

@csrf_exempt 
def createChallenge(request):

  id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
  claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
  if not claims:
    return HttpResponse('Unauthorized')
  username1 = claims['firebase']['identities']['phone']
  username = username1[0][3:13]
  if(request.method == "GET"):
    return JsonResponse({'status': 'False', 'message': 'Get request'})
  user_json_data=json.loads(request.body)

  challenge_id = str(uuid.uuid4())

  user_infoList = user_info.objects.get(username = username)

  #user_json_data[10]['challenge_to'] = "abcd"
  user_json_data['challenge_by'] = username
  user_json_data['challenge_by_name'] = user_infoList.firstname + ' '+ user_infoList.lastname
  user_json_data['challenge_id'] = challenge_id
  user_json_data['challenge_created_at'] = datetime.today().strftime("%Y-%m-%d %H:%M:%S")

  db = firestore.Client()
  doc_ref = db.collection(u'challenge').document(challenge_id)

  doc_ref.set(user_json_data)

  qs = question.objects.filter(chapter__iexact=user_json_data['chapter'], standard = user_json_data['standard']).order_by('?').values_list('xblock_id', flat=True)
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
  #return JsonResponse(thisdict)
  #doc_ref = db.collection(u'challenge_questions').document(str(user_json_data['challenge_id']))  
  #res_json = serializers.serialize('json', qs1)

  #return HttpResponse(res_json, content_type='application/json')

@csrf_exempt 
def updated_createChallenge(request):

  id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
  claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
  if not claims:
    return HttpResponse('Unauthorized')
  username = claims['firebase']['identities']['phone'][0][3:13]
  #username = "1111111133"

  student=user_info.objects.get(username=username)
  standard = student.standard
  if(standard == '13'):
    standard = 'all'

  if(request.method == "GET"):
    return JsonResponse({'status': 'False', 'message': 'Get request'})
  user_json_data=json.loads(request.body)

  challenge_id = str(uuid.uuid4())

  user_infoList = user_info.objects.get(username = username)

  #user_json_data[10]['challenge_to'] = "abcd"
  user_json_data['challenge_by'] = username
  user_json_data['challenge_by_name'] = user_infoList.firstname + ' '+ user_infoList.lastname
  user_json_data['challenge_id'] = challenge_id
  user_json_data['challenge_created_at'] = datetime.today().strftime("%Y-%m-%d %H:%M:%S")

  db = firestore.Client()
  doc_ref = db.collection(u'challenge').document(challenge_id)

  doc_ref.set(user_json_data)

  
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



@csrf_exempt
def fetchChallengequestions(request, challengeid):
  id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
  claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
  if not claims:
     return HttpResponse('Unauthorized')

  db = firestore.Client()
  doc_ref = db.collection(u'challenge_questions').document(str(challengeid))
  doc = doc_ref.get()
  allCourseBlocks = doc.to_dict()
  #return HttpResponse(list(allCourseBlocks['questions']))
  qs = question.objects.filter(xblock_id__in=list(allCourseBlocks['questions']), questionType='SMCQ')
  #qs=qs.order_by('?')[:5]

  res_json = serializers.serialize('json', qs)
  return HttpResponse(res_json, content_type='application/json')


  #res_json = json.loads(res_json)
   
  #res_json = json.dumps(res_json)

  #return HttpResponse(res_json, content_type='application/json')

  #return HttpResponse(allCourseBlocks['questions'])
  #quesList=[]
  #for document in allCourseBlocks['questions']:
  #    doc_ref = db.collection(u'ClassCast').document(document)
  #    doc = doc_ref.get()
  #    allBlocks=doc.to_dict()
  #    quesList.append(allBlocks)
        
  #return HttpResponse(json.dumps(quesList), content_type='application/json')


@csrf_exempt
def submitChallengeQuestions(request):
  id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
  claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
  if not claims:
     return HttpResponse('Unauthorized')
  if(request.method == "GET"):
    return JsonResponse({'status': 'False', 'message': 'Get request'})
  db = firestore.Client()
  user_json_data=json.loads(request.body)
  doc_ref = db.collection(u'challenge_questions').document(str(user_json_data['challenge_id']))

  if(user_json_data['status'] == 'correct'):
    score = 4
  elif(user_json_data['status'] == 'wrong'):
    score = -1
  else:
    score = 0

  if(user_json_data['is_sender']):
    doc_ref.set({
      "sender_answers": {str(user_json_data['question_index']): score}
    },  merge=True)

  else:
    doc_ref.set({
      "receiver_answers": {str(user_json_data['question_index']): score}
    },  merge=True)

  return JsonResponse(user_json_data)


@csrf_exempt
def updateChallengeRequest(request):
  id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
  claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
  if not claims:
    return HttpResponse('Unauthorized')

  if(request.method == "GET"):
    return JsonResponse({'status': 'False', 'message': 'Get request'})
  user_json_data=json.loads(request.body)
  db = firestore.Client()
  doc_ref = db.collection(u'challenge').document(str(user_json_data['challenge_id']))
  #return HttpResponse(user_json_data['received'])
  try:
    if(user_json_data['received'] == True):
      thisdict = {
        "received": True
      }
      doc_ref.set(thisdict, merge=True)
      return JsonResponse(thisdict)
  except Exception as e:
    pass


  try:
    if(user_json_data['started_by_sender'] == True):
      thisdict = {
        "started_by_sender": True,
        "started_by_sender_at": datetime.today().strftime("%Y-%m-%d %H:%M:%S")
      }
      doc_ref.set(thisdict, merge=True)
      return JsonResponse(thisdict)
  except Exception as e:
    pass

  try:
    if(user_json_data['started_by_started_by_receiver'] == True):
      thisdict = {
        "started_by_receiver": True,
        "started_by_receiver_at": datetime.today().strftime("%Y-%m-%d %H:%M:%S")
      }
      doc_ref.set(thisdict, merge=True)
      return JsonResponse(thisdict)
  except Exception as e:
    pass

  try:
    if(user_json_data['completed_by_sender'] == True):
      thisdict = {
        "completed_by_sender": True,
        "sender_marks": user_json_data['sender_marks'],
        "completed_by_sender_at": datetime.today().strftime("%Y-%m-%d %H:%M:%S")
      }
      doc_ref.set(thisdict, merge=True)
      return JsonResponse(thisdict)
  except Exception as e:
    pass

  try:
    if(user_json_data['completed_by_receiver'] == True):
      thisdict = {
        "completed_by_receiver": True,
        "receiver_marks": user_json_data['receiver_marks'],
        "completed_by_receiver_at": datetime.today().strftime("%Y-%m-%d %H:%M:%S")
      }
      doc_ref.set(thisdict, merge=True)
      return JsonResponse(thisdict)
  except Exception as e:
    pass
  return HttpResponse('nothing to update')


@csrf_exempt
def getChallengeData(request, challengeid):
  id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
  claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
  if not claims:
    return HttpResponse('Unauthorized')
  db = firestore.Client()
        
  doc_ref = db.collection(u'challenge').document(str(challengeid))
  doc = doc_ref.get()
  
  allCourseBlocks = doc.to_dict()
  this_dict = {
    "challenge_by": allCourseBlocks['challenge_by'],
    "challenge_by_name": allCourseBlocks['challenge_by_name'],
    "challenge_to": allCourseBlocks['challenge_to'],
    "challenge_to_name": allCourseBlocks['challenge_to_name'],
    "receiver_marks": allCourseBlocks['receiver_marks'],
    "sender_marks": allCourseBlocks['sender_marks']
  }
  return JsonResponse(this_dict)



