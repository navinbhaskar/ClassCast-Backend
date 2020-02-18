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
from mysite.users.models import user_info
from mysite.course_data.models import questionSagar, Classcast_test_submission, chapter, topics, student_topic_interaction, classcast_question, question
import datetime
from django.views.decorators.csrf import csrf_exempt
import random
from django.views.decorators.csrf import csrf_exempt
import google.oauth2.id_token
import google.auth.transport.requests


HTTP_REQUEST = google.auth.transport.requests.Request()

def hello(request):
   text = """<h1>welcome to my app !</h1>"""
   return HttpResponse(text)

@csrf_exempt
def gym_function(request):
   id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   if not claims:
      return HttpResponse('Unauthorized')
   username1 = claims['firebase']['identities']['phone']
   username = username1[0][3:13]
   
   #username=request.GET.get("username")
   subject=request.GET.get("subject")
   chapterList=request.GET.get("chapterList")
   standard=request.GET.get("standard")

   #username = request.POST.get('username')
   #subject = request.POST.get("subject")
   #chapterList=request.POST.get('chapter')
   #standard=request.POST.get("standard")
   
   qs = classcast_question.objects.filter(questionType='SMCQ')
   topic_list = topics.objects.all()

   n_questions=3
   correct_threshold=3
   student=user_info.objects.get(username=username)
   
   if subject is not None:
      qs = qs.filter(subject__iexact=subject)
   
   if chapterList is not None:
      qs = qs.filter(chapter__iexact=chapterList)
      
      this_chapter=chapter.objects.filter(chapter=chapterList)
      
      if this_chapter is not None:
         topic_list = topics.objects.filter(chapter__chapter=chapterList)
         #return HttpResponse(topic_list)
   if standard is not None:
      qs = qs.filter(standard=standard)
   fetch_topic=''
   fetch_difficulty=''
   
   if topic_list and chapterList is not None:
      for topic in topic_list.iterator():
         this_topic=topics.objects.get(topic_id=topic.topic_id)
         submissions_easy=student_topic_interaction.objects.filter(student=student,difficulty=1, topic=this_topic).first()
         submissions_medium=student_topic_interaction.objects.filter(student=student,difficulty=2, topic=this_topic).first()
         submissions_difficult=student_topic_interaction.objects.filter(student=student,difficulty=3, topic=this_topic).first()
         if submissions_difficult is not None: 
            if submissions_difficult.num_corrects >=correct_threshold:
               continue;
         elif submissions_medium is not None: 
            if submissions_medium.num_corrects >=correct_threshold:
               fetch_difficulty=3
               fetch_topic=topic
               break
         elif submissions_easy is not None: 
            if submissions_easy.num_corrects >=correct_threshold:
               fetch_difficulty=2
               fetch_topic=topic
               break
         else :
            fetch_difficulty=1
            fetch_topic=topic
            break       

   if fetch_topic=='' and topic_list:
      fetch_topic=random.choice(topic_list)
      fetch_difficulty=random.choice([1,2,3])
   else:
      fetch_difficulty=1

   if fetch_topic != '':
        qs1 = qs.filter(topic__iexact=fetch_topic.topic_name)
        if len(qs1)>n_questions:
            qs=qs1

   qs2=qs.filter(difficulty=fetch_difficulty)
   if len(qs2)> n_questions:
      qs=qs2
   qs=qs.order_by('?')[:(n_questions)]
   #qs = qs.values_list('xblock_id', flat=True)
   #db = firestore.Client()
   #quesList=[]
   #for document in qs:
        #return HttpResponse(document)
   #     doc_ref = db.collection(u'ClassCast').document(document)
   #     doc = doc_ref.get()
   #     allBlocks=doc.to_dict()
   #     quesList.append(allBlocks)
        
   #return HttpResponse(json.dumps(quesList), content_type='application/json')

   res_json = serializers.serialize('json', qs)
   res_json = json.loads(res_json)
   
   res_json = json.dumps(res_json)

   return HttpResponse(res_json, content_type='application/json')

   
@csrf_exempt
def new_gym_function(request):
   #id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   #claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   #if not claims:
   #   return HttpResponse('Unauthorized')
   #username1 = claims['firebase']['identities']['phone']
   #username = username1[0][3:13]
   username = '1111111133'
   #username=request.GET.get("username")
   subject=request.GET.get("subject")
   chapterList=request.GET.getlist("chapter")
   #return HttpResponse(chapterList)
   standard=request.GET.get("standard")
   qs = question.objects.filter(questionType='SMCQ')
   topic_list = topics.objects.all()

   n_questions=3
   correct_threshold=3
   student=user_info.objects.get(username=username)
   
   if subject is not None:
      qs = qs.filter(subject__iexact=subject)
   
   if chapterList is not None:
      qs = qs.filter(chapter__in=chapterList)
      
      this_chapter=chapter.objects.filter(chapter=chapterList)
      
      if this_chapter is not None:
         topic_list = topics.objects.filter(chapter__chapter=chapterList)
         #return HttpResponse(topic_list)
   if standard is not None:
      qs = qs.filter(standard=standard)
   fetch_topic=''
   fetch_difficulty=''
   
   if topic_list and chapterList is not None:
      for topic in topic_list.iterator():
         this_topic=topics.objects.get(topic_id=topic.topic_id)
         submissions_easy=student_topic_interaction.objects.filter(student=student,difficulty=1, topic=this_topic).first()
         submissions_medium=student_topic_interaction.objects.filter(student=student,difficulty=2, topic=this_topic).first()
         submissions_difficult=student_topic_interaction.objects.filter(student=student,difficulty=3, topic=this_topic).first()
         if submissions_difficult is not None: 
            if submissions_difficult.num_corrects >=correct_threshold:
               continue;
         elif submissions_medium is not None: 
            if submissions_medium.num_corrects >=correct_threshold:
               fetch_difficulty=3
               fetch_topic=topic
               break
         elif submissions_easy is not None: 
            if submissions_easy.num_corrects >=correct_threshold:
               fetch_difficulty=2
               fetch_topic=topic
               break
         else :
            fetch_difficulty=1
            fetch_topic=topic
            break       

   if fetch_topic=='' and topic_list:
      fetch_topic=random.choice(topic_list)
      fetch_difficulty=random.choice([1,2,3])
   else:
      fetch_difficulty=1

   if fetch_topic != '':
        qs1 = qs.filter(topic__iexact=fetch_topic.topic_name)
        if len(qs1)>n_questions:
            qs=qs1

   qs2=qs.filter(difficulty=fetch_difficulty)
   if len(qs2)> n_questions:
      qs=qs2
   qs=qs.order_by('?')[:(n_questions)]

   res_json = serializers.serialize('json', qs)
   res_json = json.loads(res_json)
   
   res_json = json.dumps(res_json)

   return HttpResponse(res_json, content_type='application/json')



@csrf_exempt
def updated_gym_function(request):
   id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   if not claims:
      return HttpResponse('Unauthorized')
   username1 = claims['firebase']['identities']['phone']
   username = username1[0][3:13]
   #username = '9933956490'
   #username=request.GET.get("username")
   subject=request.GET.get("subject")
   chapterList=request.GET.getlist("chapter")
   #return HttpResponse(chapterList)
   standard=request.GET.get("standard")
   qs = question.objects.filter(questionType='SMCQ')
   topic_list = topics.objects.all()

   n_questions=3
   correct_threshold=3
   student=user_info.objects.get(username=username)
   
   if subject is not None:
      qs = qs.filter(subject__iexact=subject)
   
   if chapterList is not None:
      qs = qs.filter(chapter__in=chapterList)
      
      this_chapter=chapter.objects.filter(chapter=chapterList)
      
      if this_chapter is not None:
         topic_list = topics.objects.filter(chapter__chapter=chapterList)
         #return HttpResponse(topic_list)
   if standard is not None:
      qs = qs.filter(standard=standard)
   fetch_topic=''
   fetch_difficulty=''
   
   if topic_list and chapterList is not None:
      for topic in topic_list.iterator():
         this_topic=topics.objects.get(topic_id=topic.topic_id)
         submissions_easy=student_topic_interaction.objects.filter(student=student,difficulty=1, topic=this_topic).first()
         submissions_medium=student_topic_interaction.objects.filter(student=student,difficulty=2, topic=this_topic).first()
         submissions_difficult=student_topic_interaction.objects.filter(student=student,difficulty=3, topic=this_topic).first()
         if submissions_difficult is not None: 
            if submissions_difficult.num_corrects >=correct_threshold:
               continue;
         elif submissions_medium is not None: 
            if submissions_medium.num_corrects >=correct_threshold:
               fetch_difficulty=3
               fetch_topic=topic
               break
         elif submissions_easy is not None: 
            if submissions_easy.num_corrects >=correct_threshold:
               fetch_difficulty=2
               fetch_topic=topic
               break
         else :
            fetch_difficulty=1
            fetch_topic=topic
            break       

   if fetch_topic=='' and topic_list:
      fetch_topic=random.choice(topic_list)
      fetch_difficulty=random.choice([1,2,3])
   else:
      fetch_difficulty=1

   if fetch_topic != '':
        qs1 = qs.filter(topic__iexact=fetch_topic.topic_name)
        if len(qs1)>n_questions:
            qs=qs1

   qs2=qs.filter(difficulty=fetch_difficulty)
   if len(qs2)> n_questions:
      qs=qs2
   qs=qs.order_by('?')[:(n_questions)]

   res_json = serializers.serialize('json', qs)
   res_json = json.loads(res_json)
   
   res_json = json.dumps(res_json)

   return HttpResponse(res_json, content_type='application/json')
