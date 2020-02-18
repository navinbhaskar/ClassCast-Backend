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
from mysite.course_data.models import questionSagar, Classcast_test_submission, student_topic_interaction, chapter, classcast_question, topics, question, exams_package, exams, test_sections, chapter_updated
import datetime
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
def get_chapterwise_gym_data(request):
    id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
    claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
    if not claims:
      return HttpResponse('Unauthorized')

    username = claims['firebase']['identities']['phone'][0][3:13]
    
    #username = "1111111133"
    student=user_info.objects.get(username=username)
    standard = student.standard

    goal = exam_info.objects.get(exam_id=standard)
    #ssc
    #exams_object=exams.objects.filter(course__exam_id=standard)
    index = random.randint(1,100)
    data=json.loads(request.body)

    package = data['exams_package']
    exam_name = data['exam_name']
    chapter = data['chapter']

    #exam_package_object = exams_package.objects.get(section=package)
    #ssc_cpo
    #sections = test_sections.objects.filter(exams_package = exam_package_object).values_list('section','section_name', flat=False)

    gym_data = []
    db = firestore.Client()

    quesList=[]
      
    doc_ref = db.collection(u'new_question_database').document(u'exams').collection(goal.exam_name).document(exam_name).collection(package).where(u'section', u'==', chapter).where(u'index', u'>=', index)
    doc = doc_ref.limit(5).get()
      
    for el in doc:
      quesList.append(el.to_dict())
      

    gym_data.append(
        {
          "section": chapter,
          "section_name": chapter,
          "data": quesList
        }
      )
      
    return HttpResponse(json.dumps(gym_data), content_type='application/json')


@csrf_exempt
def get_gym_data(request):
    id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
    claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
    if not claims:
      return HttpResponse('Unauthorized')

    username = claims['firebase']['identities']['phone'][0][3:13]
    
    #username = "1111111133"
    student=user_info.objects.get(username=username)
    standard = student.standard

    goal = exam_info.objects.get(exam_id=standard)
    #ssc
    #exams_object=exams.objects.filter(course__exam_id=standard)
    index = random.randint(1,100)
    data=json.loads(request.body)

    package = data['exams_package']
    exam_name = data['exam_name']
    

    exam_package_object = exams_package.objects.get(section=package)
    
    sections = test_sections.objects.filter(exams_package = exam_package_object).values_list('section','section_name', flat=False)

    #return HttpResponse(sections[0][0])
    no_of_sections = len(sections)

    section_index = random.randint(0,no_of_sections-1)

    #return HttpResponse(sections[section_index])

    test_data = []
    db = firestore.Client()

    quesList=[]
    
    doc_ref = db.collection(u'new_question_database').document(u'exams').collection(goal.exam_name).document(exam_name).collection(package).where(u'section', u'==', sections[section_index][0]).where(u'index', u'>=', index)
    doc = doc_ref.limit(5).get()
    #return HttpResponse(doc)
    #my_dict = { el.id: el.to_dict() for el in doc }
    for el in doc:
      quesList.append(el.to_dict())
    #allBlocks=doc.to_dict()
    #return HttpResponse(len(quesList))
    if(len(quesList) < 5):
      remaining_no_of_questions_per_section = 5 - len(quesList)
      doc_ref = db.collection(u'new_question_database').document(u'exams').collection(goal.exam_name).document(exam_name).collection(package).where(u'section', u'==', sections[section_index][0]).where(u'index', u'>=', 0)
      doc = doc_ref.limit(remaining_no_of_questions_per_section).get()
      for el in doc:
        quesList.append(el.to_dict())

    test_data.append(
        {
          "section": sections[section_index][0],
          "section_name": sections[section_index][1],
          "data": quesList
        }
      )
      
    return HttpResponse(json.dumps(test_data), content_type='application/json')



@csrf_exempt
def new_gym_function(request):
   id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   if not claims:
      return HttpResponse('Unauthorized')
   username1 = claims['firebase']['identities']['phone']
   username = username1[0][3:13]
   #username = '1111111133'
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
