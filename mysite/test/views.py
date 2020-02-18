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
from mysite.course_data.models import questionSagar, Classcast_test_submission, student_topic_interaction, chapter, classcast_question, question
import datetime
from django.views.decorators.csrf import csrf_exempt
import google.oauth2.id_token
import google.auth.transport.requests


HTTP_REQUEST = google.auth.transport.requests.Request()

def hello(request):
   text = """<h1>welcome to my app !</h1>"""
   return HttpResponse(text)

def test_function(request):
    id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
    claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
    if not claims:
      return HttpResponse('Unauthorized')
    qs = classcast_question.objects.filter(questionType='SMCQ')
    n_questions=request.GET.get("n_questions")
    question_type = request.GET.get("question_type")
    subject = request.GET.get("subject")
    difficulty = request.GET.get("difficulty")
    chapter=request.GET.get('chapter')
    standard=request.GET.get("standard")
    goal=request.GET.get("goal")
    topic=request.GET.get("topic")
    marks=request.GET.get("marks")
    #return HttpResponse(chapter)
    if question_type is not None:
        qs = qs.filter(question_type__iexact=question_type)
    if difficulty is not None:
        qs = qs.filter(difficulty__iexact=difficulty)
    if subject is not None:
        qs = qs.filter(subject__iexact=subject)
    if chapter is not None:
        qs = qs.filter(chapter__iexact=chapter)
    if standard is not None:
        qs = qs.filter(standard=standard)
    if goal is not None:
        qs = qs.filter(goal__iexact=goal)
    if topic is not None:
        qs = qs.filter(topic__iexact=topic)
    if n_questions is None:
        n_questions=12
    else:
        n_questions=int(n_questions)
    qs0=qs.filter(difficulty=1).order_by('?')[:(n_questions/3)]
    qs1=qs.filter(difficulty=2).order_by('?')[:(n_questions/3)]
    qs2=qs.filter(difficulty=3).order_by('?')[:(n_questions/3)]
    qs_final = list(chain(qs0, qs1, qs2))

    #db = firestore.Client()
    #quesList=[]
    #for document in qs_final:
    #    doc_ref = db.collection(u'ClassCast').document(document)
    #    doc = doc_ref.get()
    #    allBlocks=doc.to_dict()
    #    quesList.append(allBlocks)
    #    
    #return HttpResponse(json.dumps(quesList), content_type='application/json')

    if len(qs_final)!=n_questions :
        res_json = serializers.serialize('json', qs.order_by('?')[:n_questions])
    else:
        res_json = serializers.serialize('json', qs_final)
        
    return HttpResponse(res_json, content_type='application/json')


def new_test_function(request):
    id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
    claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
    if not claims:
      return HttpResponse('Unauthorized')
    qs = question.objects.filter(questionType='SMCQ')
    n_questions=request.GET.get("n_questions")
    question_type = request.GET.get("question_type")
    subject = request.GET.get("subject")
    difficulty = request.GET.get("difficulty")
    chapter=request.GET.getlist('chapter')
    standard=request.GET.get("standard")
    goal=request.GET.get("goal")
    topic=request.GET.get("topic")
    marks=request.GET.get("marks")

    single_chapter=False
    if len(chapter)==0:
        chapter=None
        single_chapter=True
    elif len(chapter)==1:
        chapter=chapter[0]
        single_chapter=True
    else:
        single_chapter=False
    #return HttpResponse(single_chapter)

    if single_chapter:
        if chapter is not None:
                qs = qs.filter(chapter__iexact=chapter)
    if not single_chapter and chapter is not None:
        qs = qs.filter(chapter__in=chapter)

    if question_type is not None:
        qs = qs.filter(question_type__iexact=question_type)
    if difficulty is not None:
        qs = qs.filter(difficulty__iexact=difficulty)
    if subject is not None:
        qs = qs.filter(subject__iexact=subject)
    #if chapter is not None:
    #    qs = qs.filter(chapter__iexact=chapter)
    if standard is not None:
        qs = qs.filter(standard=standard)
    if goal is not None:
        qs = qs.filter(goal__iexact=goal)
    if topic is not None:
        qs = qs.filter(topic__iexact=topic)
    if n_questions is None:
        n_questions=12
    else:
        n_questions=int(n_questions)
    qs0=qs.filter(difficulty=1).order_by('?')[:(n_questions/3)]
    qs1=qs.filter(difficulty=2).order_by('?')[:(n_questions/3)]
    qs2=qs.filter(difficulty=3).order_by('?')[:(n_questions/3)]
    qs_final = list(chain(qs0, qs1, qs2))

    #return HttpResponse(res_json['question'], content_type='application/json')

    if len(qs_final)!=n_questions :
        res_json = serializers.serialize('json', qs.order_by('?')[:n_questions])
    else:
        res_json = serializers.serialize('json', qs_final)
        
    return HttpResponse(res_json, content_type='application/json')


def updated_test_function(request):
    id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
    claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
    if not claims:
      return HttpResponse('Unauthorized')
    qs = question.objects.filter(questionType='SMCQ')
    n_questions=request.GET.get("n_questions")
    question_type = request.GET.get("question_type")
    subject = request.GET.get("subject")
    difficulty = request.GET.get("difficulty")
    chapter=request.GET.getlist('chapter')
    standard=request.GET.get("standard")
    goal=request.GET.get("goal")
    topic=request.GET.get("topic")
    marks=request.GET.get("marks")

    single_chapter=False
    if len(chapter)==0:
        chapter=None
        single_chapter=True
    elif len(chapter)==1:
        chapter=chapter[0]
        single_chapter=True
    else:
        single_chapter=False
    #return HttpResponse(single_chapter)

    if single_chapter:
        if chapter is not None:
                qs = qs.filter(chapter__iexact=chapter)
    if not single_chapter and chapter is not None:
        qs = qs.filter(chapter__in=chapter)

    if question_type is not None:
        qs = qs.filter(question_type__iexact=question_type)
    if difficulty is not None:
        qs = qs.filter(difficulty__iexact=difficulty)
    if subject is not None:
        qs = qs.filter(subject__iexact=subject)
    #if chapter is not None:
    #    qs = qs.filter(chapter__iexact=chapter)
    if standard is not None:
        qs = qs.filter(standard=standard)
    if goal is not None:
        qs = qs.filter(goal__iexact=goal)
    if topic is not None:
        qs = qs.filter(topic__iexact=topic)
    if n_questions is None:
        n_questions=12
    else:
        n_questions=int(n_questions)
    qs0=qs.filter(difficulty=1).order_by('?')[:(n_questions/3)]
    qs1=qs.filter(difficulty=2).order_by('?')[:(n_questions/3)]
    qs2=qs.filter(difficulty=3).order_by('?')[:(n_questions/3)]
    qs_final = list(chain(qs0, qs1, qs2))

    #return HttpResponse(res_json['question'], content_type='application/json')

    if len(qs_final)!=n_questions :
        res_json = serializers.serialize('json', qs.order_by('?')[:n_questions])
    else:
        res_json = serializers.serialize('json', qs_final)
        
    return HttpResponse(res_json, content_type='application/json')



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

