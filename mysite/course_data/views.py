import os
import sys
from django.shortcuts import render
from rest_framework.views import APIView
from django.http import HttpResponse
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status
import datetime
from firebase_admin import firestore
import json
from .serializers import chapterlistSerializer
from .models import chapter, chapter_updated
import google.oauth2.id_token
import google.auth.transport.requests
from django.views.decorators.csrf import csrf_exempt
import base64
import time
import urllib
from datetime import datetime, timedelta, date
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
import base64
from OpenSSL import crypto
from mysite.settings import BASE_DIR
from django.core import serializers
sys.path.append("..")
from mysite.users.models import user_info, exam_info
import csv
from mysite.course_data.models import classcast_question, student_block_interactions, question, questionSagar, exams, exams_package, chapter_updated, chapter
#path = XMLFILES_FOLDER+'classcast-198812-f514111c8d53.p12'


HTTP_REQUEST = google.auth.transport.requests.Request()

class fetchChapterBlocks(APIView):
    def get(self, request, course_id, chapter_id):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')

        db = firestore.Client()
        #doc = db.collection(u'courseDatabase').document(subject).collection(courseid).where(u'block_type', u'==', 'video')
        #doc1 = doc.order_by(u'ranking').get()
        #my_dict = { el.id: el.to_dict() for el in doc1 }
        
        doc_ref = db.collection(u'courses').document(course_id).collection(chapter_id).document(chapter_id)
        doc = doc_ref.get()
        allCourseBlocks = doc.to_dict()
        #doc = db.collection(u'courseDatabase').document(subject).collection(courseid)
        #doc1 = doc.get()
        #my_dict = { el.id: el.to_dict() for el in doc1 }
        return JsonResponse(allCourseBlocks)

class fetchCourseBlocks(APIView):
    def get(self, request, courseid):
        #id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        #claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        #if not claims:
        #    return HttpResponse('Unauthorized')

        if(courseid[0:2] == 'MA'):
            subject = 'Mathematics'
        elif(courseid[0:2] == 'CH'):
            subject = 'Chemistry'
        elif(courseid[0:2] == 'PH'):
            subject = 'Physics'
        else:
            subject = 'Null'

        db = firestore.Client()
        #doc = db.collection(u'courseDatabase').document(subject).collection(courseid).where(u'block_type', u'==', 'video')
        #doc1 = doc.order_by(u'ranking').get()
        #my_dict = { el.id: el.to_dict() for el in doc1 }
        
        doc_ref = db.collection(u'courseDatabase').document(subject).collection(courseid).document(courseid)
        doc = doc_ref.get()
        allCourseBlocks = doc.to_dict()
        #doc = db.collection(u'courseDatabase').document(subject).collection(courseid)
        #doc1 = doc.get()
        #my_dict = { el.id: el.to_dict() for el in doc1 }
        return JsonResponse(allCourseBlocks)


class chapterlist(APIView):
    def get(self, request, standard, subject):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')

        username1 = claims['firebase']['identities']['phone']
        username = username1[0][3:13]
        #username='1111111122'
        student=user_info.objects.get(username=username)
        standard = student.standard
        if(standard == '13'):
          standard = 'all'
        if(subject == 'Mathematics'):
            subject = 'Maths'

        if not chapter(standard = standard):
                return Response('Standard not found', status= status.HTTP_400_BAD_REQUEST)
        if not chapter(subject =subject):
                return Response('Subject not found', status= status.HTTP_400_BAD_REQUEST)
        if standard=="all":
                chapterlist3 = chapter.objects.filter(subject=subject)
                serializer=chapterlistSerializer(chapterlist3, many=True)
                return Response(serializer.data)
        
        chapterlist = chapter.objects.filter(standard=standard, subject=subject)
        serializer=chapterlistSerializer(chapterlist, many=True)
        return Response(serializer.data)


class updated_chapterlist(APIView):
    def get(self, request, subject):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')

        username1 = claims['firebase']['identities']['phone']
        username = username1[0][3:13]
        #username='1111111188'
        student=user_info.objects.get(username=username)
        standard = student.standard
        if(standard == 'all'):
          	standard = 'all'
        if(subject == 'Mathematics'):
            subject = 'Maths'
        #return HttpResponse(claims['firebase']['identities']['phone'])
        if not chapter(standard = standard):
                return Response('Standard not found', status= status.HTTP_400_BAD_REQUEST)
        if not chapter(subject =subject):
                return Response('Subject not found', status= status.HTTP_400_BAD_REQUEST)
        if standard=="all":
                chapterlist3 = chapter.objects.filter(subject=subject)
                serializer=chapterlistSerializer(chapterlist3, many=True)
                return Response(serializer.data)
        
        if(standard == '13'):
        	chapterlist = chapter.objects.filter(standard__in=['11','12'], subject=subject)
	        serializer=chapterlistSerializer(chapterlist, many=True)
	        return Response(serializer.data)		

        chapterlist = chapter.objects.filter(standard=standard, subject=subject)
        serializer=chapterlistSerializer(chapterlist, many=True)
        return Response(serializer.data)

@csrf_exempt
def fetchAssignmentQuestions(request):
  id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
  claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
  if not claims:
     return HttpResponse('Unauthorized')

  if(request.method == "GET"):
    return JsonResponse({'status': 'False', 'message': 'Get request'})

  user_json_data=json.loads(request.body)
  block_id_list = user_json_data['block_id'];
    
  #return HttpResponse(block_id_list)  
  qs = question.objects.filter(xblock_id__in=block_id_list)
  
  #qs=qs.order_by('?')[:5]

  res_json = serializers.serialize('json', qs)
  return HttpResponse(res_json, content_type='application/json')

@csrf_exempt
def storeStudentBlockInteractions(request):
  id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
  claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
  if not claims:
     return HttpResponse('Unauthorized')

  if(request.method == "GET"):
    return JsonResponse({'status': 'False', 'message': 'Get request'})

  username1 = claims['firebase']['identities']['phone']
  username = username1[0][3:13]
  #username='1111111122'
  student=user_info.objects.get(username=username)

  user_json_data=json.loads(request.body)
  course_id = user_json_data['course_id']
  block_id = user_json_data['block_id']

  if(student_block_interactions.objects.filter(student=student, course_id = course_id, block = block_id).exists()):
    return HttpResponse('Entry Already Exists', status= 201)
  else:
    student_block_interactions_object=student_block_interactions(student=student, course_id = course_id, block = block_id)
    student_block_interactions_object.save()
    return HttpResponse('Updated', status= 201)


@csrf_exempt
def storeScoreFromCourseBlocks(request):
  id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
  claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
  if not claims:
     return HttpResponse('Unauthorized')

  if(request.method == "GET"):
    return JsonResponse({'status': 'False', 'message': 'Get request'})

  username1 = claims['firebase']['identities']['phone']
  username = username1[0][3:13]
  student=user_info.objects.get(username=username)

  user_json_data=json.loads(request.body)
  course_id = user_json_data['course_id']
  block_id = user_json_data['block_id']
  points = user_json_data['points']

  if(student_block_interactions.objects.filter(student=student, course_id = course_id, block = block_id).exists()):
    return HttpResponse('Entry Already Exists', status= 201)
  else:
    student_block_interactions_object=student_block_interactions(student=student, course_id = course_id, block = block_id)
    student_block_interactions_object.save()
    db = firestore.Client()
    today_date=date.today()
    doc_ref = db.collection(u'performance').document(username)
    doc = doc_ref.get()
    allCourseBlocks = doc.to_dict()


    try:
      totalPoints = sum(allCourseBlocks.values())
    except:
      totalPoints = 0 
    #student_info = user_info.objects.get(username=username)
    student.karma_point = int(points) + int(totalPoints);
    student.save()

    try:
        score = allCourseBlocks[str(today_date)]
    except:
        score = 0

    totalScore = int(score) + int(points)
    thisdict =  {
      str(today_date): totalScore
    }

    doc_ref = db.collection(u'performance').document(username)
    doc_ref.set(thisdict, merge=True)

  return HttpResponse('Updated', status= 201)


@csrf_exempt
def generateSignedUrl(request):
    #id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
    #claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
    #if not claims:
    #    return HttpResponse('Unauthorized')

    user_json_data=json.loads(request.body)
    resource = user_json_data['path'];

    method = 'GET'
    
    content_md5, content_type = None, None

    expiration = datetime.utcnow() + timedelta(hours=11)
    expiration = int(time.mktime(expiration.timetuple()))

    signature_string = '\n'.join([
      method,
      content_md5 or '',
      content_type or '',
      str(expiration),
      resource])

    path = os.path.join(os.path.split(__file__)[0], 'classcast-198812-f514111c8d53.p12')
    #return HttpResponse(path)
    #path = BASE_DIR+'\\mysite\\course_data\\classcast-198812-f514111c8d53.p12'
    private_key = open(path, 'rb').read()
    pkcs12 = crypto.load_pkcs12(private_key, 'notasecret')
    pem = crypto.dump_privatekey(crypto.FILETYPE_PEM, pkcs12.get_privatekey())
    pem_key = RSA.importKey(pem)

    signer = PKCS1_v1_5.new(pem_key)
    signature_hash = SHA256.new(signature_string.encode('utf-8'))
    signature_bytes = signer.sign(signature_hash)
    signature = base64.b64encode(signature_bytes)

    query_params = {'GoogleAccessId': 'classcast-198812@appspot.gserviceaccount.com', 'Expires': str(expiration), 'Signature': signature}

    url = '{endpoint}{resource}?{querystring}'.format(endpoint="https://storage.googleapis.com", resource=resource,querystring=urllib.parse.urlencode(query_params))
    return HttpResponse(url)


@csrf_exempt
def uploadQuestions(request):
	failed = 0
	path = os.path.join(os.path.split(__file__)[0], 'combined_all_csv.csv')
	with open(path, encoding="utf8") as f:
		reader = csv.reader(f)
		for row in reader:
			try:
				class_attendance=question(xblock_id=row[0], goal=row[1], standard=row[2], subject=row[3], chapter=row[4], topic=row[5], difficulty=row[6], marks=row[7], negativeMarks=row[8], questionType=row[9], tags=row[10], question=row[11], option1=row[12], option2=row[13], option3=row[14], option4=row[15], option1_iscorrect=row[16], option2_iscorrect=row[17], option3_iscorrect=row[18], option4_iscorrect=row[19], explanation=row[20])
				class_attendance.save()
			except:
				failed += 1
				pass
  
	return JsonResponse({'status': 'True', 'message': 'Successfully updated', 'failed': failed})


@csrf_exempt
def testGoalAndSubjectList(request):
	id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
	claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
	if not claims:
	 return HttpResponse('Unauthorized')

	if(request.method == "POST"):
		return JsonResponse({'status': 'False', 'message': 'Get request'})

	username1 = claims['firebase']['identities']['phone']
	username = username1[0][3:13]
	
	student=user_info.objects.get(username=username)
	standard = student.standard
	
	if(standard == '11' or standard == '12' or standard == '13'):
		return JsonResponse({'subjects': [{'index': 0,'name': 'Physics'},{'index': 1,'name': 'Chemistry'},{'index': 2,'name': 'Mathematics'}], 'goal': [{'index': 0,'name': 'CBSE'},{'index': 1, 'name': 'JEE-MAINS'},{'index': 2, 'name': 'JEE-ADVANCED'}]})

	elif(standard == '9' or standard == '10'):
		return JsonResponse({'subjects': [{'index': 3,'name': 'Science'},{'index': 2,'name': 'Mathematics'}], 'goal': [{'index': 0, 'name': 'CBSE'}]})

	else:
		return JsonResponse({'subjects': [], 'goal': []})		


@csrf_exempt
def update_chapterdata(request):
  #id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
  #claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
  #if not claims:
  #   return HttpResponse('Unauthorized')

  #if(request.method == "GET"):
  #  return JsonResponse({'status': 'False', 'message': 'Get request'})

  #username1 = claims['firebase']['identities']['phone']
  #username = username1[0][3:13]
  #student=user_info.objects.get(username=username)

  user_json_data=json.loads(request.body)
  course_number = user_json_data['course_number']
  goal = user_json_data['goal']
  subject = user_json_data['subject']
  subject_name_in_database = user_json_data['subject_name_in_database']



  chapter_list = chapter.objects.filter(standard=course_number, subject=subject_name_in_database).values_list('chapter', flat=True)

  #return HttpResponse(chapter_list[0])
  for chap in chapter_list:
    try:
      course_object = exam_info.objects.get(exam_id="13")

      exams_object=exams.objects.get(course=course_object, exam_name = goal)

      section_object=exams_package.objects.get(exam=exams_object, section=subject)

      chapter_object=chapter_updated(course=course_object, exam = exams_object, exams_package=section_object, chapter=chap)
      chapter_object.save()
    except:
      pass

  return HttpResponse("Updated")


class myTests(APIView):
    def get(self, request, teacher_id):
      id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
      claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
      if not claims:
        return HttpResponse('Unauthorized')

      if(request.method == "POST"):
        return JsonResponse({'status': 'False', 'message': 'Get request'})

      username = claims['firebase']['identities']['phone'][0][3:13]
      #username = "1111111133"
      db = firestore.Client()
      doc_ref = db.collection(u'test').where(u'participants', u'array_contains', username).where(u'send_by_id', u'==', teacher_id)

      doc = doc_ref.get()

      testList = []

      try:
          section = all_data['sections']
      except:
          section = []

      for el in doc:
          all_data = el.to_dict()
          data = {
              "test_id": all_data['test_id'],
              "exam_name": all_data['exam_name'],
              "package": all_data['package'],
              "class": all_data['class'],
              "sections": all_data['sections'],
              "batch_id": all_data['batch_id'],
              "time": all_data['test_time']
          }
          testList.append(data)

      return HttpResponse(json.dumps(testList), content_type='application/json')

@csrf_exempt
def store_discussion_data(request):
  id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
  claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
  if not claims:
     return HttpResponse('Unauthorized')
  username = claims['firebase']['identities']['phone'][0][3:13]
  #username = "1111111133"

  if(request.method == "GET"):
    return JsonResponse({'status': 'False', 'message': 'Get request'})

  user_json_data=json.loads(request.body)
  course_id = user_json_data['course_id'];
  text = user_json_data['text'];
  time = user_json_data['time'];
    
  student_info = user_info.objects.get(username=username)
  name = student_info.firstname
  
  db = firestore.Client()

  if(course_id[0:2] == 'MA'):
    subject = 'Mathematics'
  elif(course_id[0:2] == 'CH'):
    subject = 'Chemistry'
  elif(course_id[0:2] == 'PH'):
    subject = 'Physics'
  else:
    subject = 'Null'

  doc_ref = db.collection(u'courseDatabase').document(subject).collection(course_id).document(course_id)

  data = {
            "name": name,
            "username": username,
            "text": text,
            "time": time
        }
  doc_ref.update({u'discussions': firestore.ArrayUnion([data])})

  return HttpResponse('Updated', status= 201)

@csrf_exempt
def store_block_discussion_data(request):
  id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
  claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
  if not claims:
     return HttpResponse('Unauthorized')
  username = claims['firebase']['identities']['phone'][0][3:13]
  #username = "1111111133"

  if(request.method == "GET"):
    return JsonResponse({'status': 'False', 'message': 'Get request'})

  user_json_data=json.loads(request.body)
  block_id = user_json_data['block_id'];
  text = user_json_data['text'];
  time = user_json_data['time'];
    
  student_info = user_info.objects.get(username=username)
  name = student_info.firstname
  
  db = firestore.Client()

  doc_ref = db.collection(u'discussion').document(block_id)

  data = {
            "name": name,
            "username": username,
            "text": text,
            "datetime": time
        }
  doc_ref.update({u'comments': firestore.ArrayUnion([data])})

  return HttpResponse('Updated', status= 201)