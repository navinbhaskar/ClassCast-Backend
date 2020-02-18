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

def test_function(request):
    
    db = firestore.Client()
    quesList=[]
    
    doc_ref = db.collection(u'new_question_database').document(u'exams').collection(u'SSC').document(u'SSC CPO').collection(u'SSC CPO 2018 Paper 1 Pack').where(u'section', u'==', u'English').where(u'isNum', u'==', False)
    doc = doc_ref.limit(5).get()
    #my_dict = { el.id: el.to_dict() for el in doc }
    for el in doc:
      quesList.append(el.to_dict())
    #allBlocks=doc.to_dict()
    
    return HttpResponse(json.dumps(quesList), content_type='application/json')


@csrf_exempt
def newsubmission(request):
   id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   if not claims:
      return HttpResponse('Unauthorized')

   if(request.method == "GET"):
      return JsonResponse({'status': 'False', 'message': 'Get request'})
   username = request.POST.get('username')
   xblock_id = request.POST.get('xblock_id')
   attempted = request.POST.get('attempted')
   correctly_attempted = request.POST.get('correctly_attempted')
   num_skips = request.POST.get('num_skips')
   time_taken = request.POST.get('time_taken')
   attempted_in_test = request.POST.get('attempted_in_test')
   attempted_in_gym = request.POST.get('attempted_in_gym')
   timestamp = str(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"))
   
   student=user_info.objects.get(username=username)
   xblock=questionSagar.objects.get(xblock_id=xblock_id)
   try:
      topic = xblock.topic
   except:
      topic = ''
   try:
      difficulty = xblock.difficulty
   except:
      difficulty = 1
   if student_topic_interaction.objects.filter(student=student, xblock_id=xblock_id, attempted_in_test=attempted_in_test).exists():
      entry = student_topic_interaction.objects.get(student=student, xblock_id=xblock_id, attempted_in_test=attempted_in_test)
      student_topic_interaction.objects.filter(student=student, xblock_id=xblock_id, attempted_in_test=attempted_in_test).update(attempted=entry.attempted+1)
      student_topic_interaction.objects.filter(student=student, xblock_id=xblock_id, attempted_in_test=attempted_in_test).update(time_taken=entry.time_taken+int(time_taken))
      #Classcast_question_submission.objects.filter(student=student, xblock_id=xblock_id, attempted_in_test=attempted_in_test).update(timestamp=timestamp)
      if(correctly_attempted == '1'):
         student_topic_interaction.objects.filter(student=student, xblock_id=xblock_id, attempted_in_test=attempted_in_test).update(correctly_attempted=entry.correctly_attempted+1)  
      elif(num_skips==1):
         student_topic_interaction.objects.filter(student=student, xblock_id=xblock_id, attempted_in_test=attempted_in_test).update(num_skips=entry.num_skips+1)
      else:
         pass
      return JsonResponse({'status': 'True', 'message': 'Updated'})
   
   try:
      sub = student_topic_interaction(student=student, 
                                           xblock=xblock, attempted=attempted, num_skips=num_skips,
                                           topic=topic, difficulty=difficulty,
                                           correctly_attempted =correctly_attempted, time_taken=time_taken,
                                           attempted_in_test=attempted_in_test, 
                                           attempted_in_gym=attempted_in_gym, timestamp=timestamp)
      sub.save()
      return JsonResponse({'status': 'True', 'message': 'Success'})

   except Exception as e:
      return JsonResponse({'status': 'False', 'message': 'Some error occured,: {}'.format(e)})


@csrf_exempt
def newTestSubmission(request):
   if(request.method == "GET"):
      return JsonResponse({'status': 'False', 'message': 'Get request'})
   username = request.POST.get('username')
   chapterName = request.POST.get('chapter')
   n_questions = request.POST.get('n_questions')
   score = request.POST.get('score')
   time_taken = request.POST.get('time_taken')
   timestamp = str(datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S"))
   
   student=user_info.objects.get(username=username)
   chapter1=chapter.objects.get(chapter=chapterName)


   try:
      sub = Classcast_test_submission(student=student, chapter=chapter1, n_questions=n_questions,
                                      score=score, time_taken=time_taken, timestamp=timestamp)

      sub.save()
      return JsonResponse({'status': 'True', 'message': 'Success'})

   except Exception as e:
      return JsonResponse({'status': 'False', 'message': 'Some error occured,: {}'.format(e)})

def exams_list(request):
    id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
    claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
    if not claims:
      return HttpResponse('Unauthorized')
    username = claims['firebase']['identities']['phone'][0][3:13]
    
    #username = "1111111133"
    student=user_info.objects.get(username=username)

    standard = student.standard

    exams_object=exams.objects.filter(course__exam_id=standard)

    test_info = []

    for exam in exams_object:
      exams_object=exams_package.objects.filter(exam=exam)
      package_dict = []
      
      exam_name = exam.exam_name
      url = exam.image_url

      for package in exams_object:
        data1 = {
          "name": package.section,
          "image": package.image_url,
          "topic_available": package.topic_available
        }
        package_dict.append(data1)
        
      data = {
        "name": exam_name,
        "image": url,
        "package": package_dict
      }
      test_info.append(data)

    return HttpResponse(json.dumps(test_info), content_type='application/json')

@csrf_exempt
def get_test_data(request):
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
    duration = data['duration']
    
    if(duration == 30):
      no_of_questions_per_section = 10
    else:
      no_of_questions_per_section = 20

    exam_package_object = exams_package.objects.get(section=package)
    #ssc_cpo
    sections = test_sections.objects.filter(exams_package = exam_package_object).values_list('section','section_name', flat=False)

    test_data = []
    db = firestore.Client()

    for i in sections:
      quesList=[]
      
      doc_ref = db.collection(u'new_question_database').document(u'exams').collection(goal.exam_name).document(exam_name).collection(package).where(u'section', u'==', i[0]).where(u'index', u'>=', index)
      doc = doc_ref.limit(no_of_questions_per_section).get()
      #return HttpResponse(doc)
      #my_dict = { el.id: el.to_dict() for el in doc }
      for el in doc:
        quesList.append(el.to_dict())
      #allBlocks=doc.to_dict()
      #return HttpResponse(len(quesList))
      if(len(quesList) < no_of_questions_per_section):
        remaining_no_of_questions_per_section = no_of_questions_per_section - len(quesList)
        doc_ref = db.collection(u'new_question_database').document(u'exams').collection(goal.exam_name).document(exam_name).collection(package).where(u'section', u'==', i[0]).where(u'index', u'>=', 0)
        doc = doc_ref.limit(remaining_no_of_questions_per_section).get()
        for el in doc:
          quesList.append(el.to_dict())

      test_data.append(
          {
            "section": i[0],
            "section_name": i[1],
            "data": quesList
          }
        )
      
    return HttpResponse(json.dumps(test_data), content_type='application/json')

@csrf_exempt
def get_chapterwise_test_data(request):
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
    duration = data['duration']
    sections = data['chapters']
    
    if(duration == 30):
      no_of_questions_per_section = 10
    else:
      no_of_questions_per_section = 20

    #exam_package_object = exams_package.objects.get(section=package)
    #ssc_cpo
    #sections = test_sections.objects.filter(exams_package = exam_package_object).values_list('section','section_name', flat=False)

    test_data = []
    db = firestore.Client()

    for i in sections:
      quesList=[]
      
      doc_ref = db.collection(u'new_question_database').document(u'exams').collection(goal.exam_name).document(exam_name).collection(package).where(u'section', u'==', i).where(u'index', u'>=', index)
      doc = doc_ref.limit(no_of_questions_per_section).get()
      #return HttpResponse(doc)
      #my_dict = { el.id: el.to_dict() for el in doc }
      for el in doc:
        quesList.append(el.to_dict())
      #allBlocks=doc.to_dict()
      #return HttpResponse(len(quesList))
      if(len(quesList) < no_of_questions_per_section):
        remaining_no_of_questions_per_section = no_of_questions_per_section - len(quesList)

        doc_ref = db.collection(u'new_question_database').document(u'exams').collection(goal.exam_name).document(exam_name).collection(package).where(u'section', u'==', i).where(u'index', u'>=', 0)
        doc = doc_ref.limit(remaining_no_of_questions_per_section).get()
       	for el in doc:
          quesList.append(el.to_dict())
      
      if(len(quesList) < no_of_questions_per_section):

        remaining_no_of_questions_per_section = no_of_questions_per_section - len(quesList)

        museums = db.collection_group(package).where(u'section', u'==', i)

        docs = museums.limit(remaining_no_of_questions_per_section).stream()

        for doc in docs:
          quesList.append(doc.to_dict())


      test_data.append(
          {
            "section": i,
            "section_name": i,
            "data": quesList
          }
        )
      
    return HttpResponse(json.dumps(test_data), content_type='application/json')

      


@csrf_exempt
def get_topic_list(request):
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
    data=json.loads(request.body)

    package = data['exams_package']
    exam_name = data['exam_name']

    chapter_list = chapter_updated.objects.filter(course = goal, exam__exam_name = exam_name, exams_package__section = package).values_list('chapter', flat=True)

    data = []

    for chapter in chapter_list:
      chapter_data = {
        "name": chapter,
      }

      data.append(chapter_data)

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def save_test_performance(request):
    id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
    claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
    if not claims:
      return HttpResponse('Unauthorized')

    username = claims['firebase']['identities']['phone'][0][3:13]
    
    #username = "1111111133"
    student=user_info.objects.get(username=username)
    standard = student.standard
    goal = exam_info.objects.get(exam_id=standard)


    data=json.loads(request.body)

    db = firestore.Client()

    for section in data['data']:
      doc_ref = db.collection(u'test_performance').document(str(uuid.uuid4()))
      section['username'] = username
      section['exam_name'] = data['goal']
      section['subject'] = data['subject']
      section['exam'] = goal.exam_name
      doc_ref.set(section, merge=True)

    return HttpResponse('Updated')


@csrf_exempt
def save_test_performance_updated(request):
    id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
    claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
    if not claims:
      return HttpResponse('Unauthorized')

    username = claims['firebase']['identities']['phone'][0][3:13]
    
    #username = "1111111133"
    student=user_info.objects.get(username=username)
    standard = student.standard
    goal = exam_info.objects.get(exam_id=standard)


    data=json.loads(request.body)

    db = firestore.Client()

    for section in data['data']:
      doc_ref = db.collection(u'test_performance').document(str(uuid.uuid4()))
      section['username'] = username
      section['test_id'] = data['test_id']
      section['exam_name'] = data['goal']
      section['subject'] = data['subject']
      section['exam'] = goal.exam_name
      doc_ref.set(section, merge=True)

    return HttpResponse('Updated')


@csrf_exempt
def view_attempted_test(request, test_id):
    id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
    claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
    if not claims:
      return HttpResponse('Unauthorized')

    username = claims['firebase']['identities']['phone'][0][3:13]
    
    #username = "1111111133"

    db = firestore.Client()

    docs = db.collection(u'test_records').where(u'test_id', u'==', test_id).where(u'username', u'>=', username).stream()

    data = []

    for doc in docs:
      data.append(doc.to_dict())
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def save_test_data(request):
    id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
    claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
    if not claims:
      return HttpResponse('Unauthorized')

    username = claims['firebase']['identities']['phone'][0][3:13]
    
    #username = "1111111133"

    data=json.loads(request.body)
    data['username'] = username

    db = firestore.Client()

    doc_ref = db.collection(u'test_records').document(str(uuid.uuid4()))
    doc_ref.set(data, merge=True)

    return HttpResponse('Updated')