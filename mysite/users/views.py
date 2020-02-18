from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from .models import user_info, exam_info, parents_details
import json
import google.oauth2.id_token
import google.auth.transport.requests
import sys
from rest_framework.response import Response
sys.path.append("..")
from mysite.teachers.models import teacher_student_interaction
from firebase_admin import firestore
from django.core import serializers
from itertools import groupby

HTTP_REQUEST = google.auth.transport.requests.Request()


def hello(request):
   text = """<h1>welcome to Bandersnatch !</h1>"""
   return HttpResponse(text)

@csrf_exempt
def updateprofile(request):
   id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   if not claims:
      return HttpResponse('Unauthorized')
   user_json_data=json.loads(request.body)
   username = user_json_data['username'];
   
   if user_info.objects.filter(username=username).exists():
      student_info = user_info.objects.get(username=username)
      try:
         if user_json_data['standard'] is not None:
            student_info.standard = user_json_data['standard'];
      except Exception as e:
         pass;
      
      try:
         if user_json_data['stream'] is not None:
            student_info.stream = user_json_data['stream'];
      except Exception as e:
         pass;
      
      try:
         if user_json_data['coachings'] is not None:
            student_info.coachings = user_json_data['coachings'];
      except Exception as e:
         pass;
      
      try:
         if user_json_data['goal'] is not None:
            student_info.goal = user_json_data['goal'];
      except Exception as e:
         pass;
      student_info.save()
      return JsonResponse({'status': 'True', 'message': 'Successfully updated'})
   
   firstname = user_json_data['firstname'];
   lastname = user_json_data['lastname'];
   gender = user_json_data['gender'];
   standard = user_json_data['standard'];
   phone_number = user_json_data['phone_number'];
   email = user_json_data['email'];
   
   try:
      userData = user_info(firstname=firstname,
                           lastname=lastname,
                           gender=gender,
                           standard=standard,
                           phone_number=phone_number,
                           username=username,
                           email = email,
                           date_joined=datetime.today(),
                           )
      
      userData.save()
      return JsonResponse({'status': 'True', 'message': 'Successfully created'})
   except Exception as e:
      return HttpResponse(e)

@csrf_exempt
def verify_profile(request):
   id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   if not claims:
      return HttpResponse('Unauthorized')
   
   username1 = claims['firebase']['identities']['phone']
   username = username1[0][3:13]
   
   if user_info.objects.filter(username=username).exists():
      return HttpResponse('authorized', status= 201)
   return HttpResponse('unauthorized', status=401)



@csrf_exempt
def complete_profile(request):
   id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   if not claims:
      return HttpResponse('Unauthorized')
   user_json_data=json.loads(request.body)
   username = claims['firebase']['identities']['phone'][0][3:13]
   
   if user_info.objects.filter(username=username).exists():
      student_info = user_info.objects.get(username=username)
      try:
         if user_json_data['area'] is not None:
            student_info.area = user_json_data['area'];
      except Exception as e:
         pass;
      
      try:
         if user_json_data['pincode'] is not None:
            student_info.pincode = user_json_data['pincode'];
      except Exception as e:
         pass;
      
      try:
         if user_json_data['photo'] is not None:
            student_info.photo = user_json_data['photo'];
      except Exception as e:
         pass;
      
      try:
         if user_json_data['school'] is not None:
            student_info.school = user_json_data['school'];
      except Exception as e:
         pass;
      
      try:
         if user_json_data['dob'] is not None:
            student_info.dob = user_json_data['dob'];
      except Exception as e:
         pass;
         
      try:
         if user_json_data['coachings'] is not None:
            student_info.coachings = user_json_data['coachings'];
      except Exception as e:
         pass;

      try:
         if user_json_data['language'] is not None:
            student_info.language = user_json_data['language'];
      except Exception as e:
         pass;
      student_info.save()
      return JsonResponse({'status': 'True', 'message': 'Successfully updated'})
   else:
      return JsonResponse({'status': 'False', 'message': 'User Does Not Exist'})



@csrf_exempt
def announcements(request):
   id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   if not claims:
      return HttpResponse('Unauthorized')
   #user_json_data=json.loads(request.body)
   #username = user_json_data['student'];
   username1 = claims['firebase']['identities']['phone']
   username = username1[0][3:13]

   student = user_info.objects.get(username=username)
   standard = student.standard
   #return HttpResponse(student.standard)
   #username = '1111111122'
   myTeachersList = teacher_student_interaction.objects.filter(student__username = username, is_active = True).values_list('teacher__teacher_id', 'teacher__firstname', 'teacher__lastname', 'batch_id', 'teacher__photo', flat=False)

   #return HttpResponse(myTeachersList)
   arr=[]
   db = firestore.Client()
   for teacherIndex in range(len(myTeachersList)):
      docs = db.collection(u'announcement').document(myTeachersList[teacherIndex][0]).collection(myTeachersList[teacherIndex][3]).get()
      for doc in docs:
         a = doc.to_dict()
         
         if(int(standard) in a['class']):
            data = {
               "firstname": myTeachersList[teacherIndex][1],
               "lastname": myTeachersList[teacherIndex][2],
               "photo": myTeachersList[teacherIndex][4],
               "time": str(a['time']),
               "message": a['message'],
               "type": a['type']
            }
            arr.append(data)
         #arr1 = u'{}'.format(doc.to_dict())
         #arr.append(json.dumps(arr1))
   s = sorted(arr, key=lambda k: k.get('time', 0), reverse=True)
   return HttpResponse(json.dumps(s),  content_type="application/json")


def userlist(request):
   teacher_id=request.GET.get("teacher_id")
   batch_id=request.GET.get("batch_id")
   standard=request.GET.get("standard")

   if((teacher_id is not None) and (batch_id is not None)):
      username_list=[]
      studentList = teacher_student_interaction.objects.select_related('student').filter(teacher__teacher_id=teacher_id, batch_id=batch_id)
      for book in studentList:
         if(standard is not None):
            if(standard == 'all'):
               username_list.append(book.student.username)
            elif(standard == book.student.standard):
               username_list.append(book.student.username)
            else:
               pass; 
         else:
            username_list.append(book.student.username)
      return JsonResponse(list(username_list), safe=False)
      #return HttpResponse(username_list, status= 201)

   elif(teacher_id is not None):
      studentList = teacher_student_interaction.objects.select_related('student').filter(teacher__teacher_id=teacher_id)
      for book in studentList:
         if(standard is not None):
            if(standard == 'all'):
               username_list.append(book.student.username)
            elif(standard == book.student.standard):
               username_list.append(book.student.username)
            else:
               pass; 
         else:
            username_list.append(book.student.username)
      return HttpResponse(username_list, status= 201)
   else:
      studentList = teacher_student_interaction.objects.select_related('student').all()
      for book in studentList:
         if(standard is not None):
            if(standard == 'all'):
               username_list.append(book.student.username)
            elif(standard == book.student.standard):
               username_list.append(book.student.username)
            else:
               pass; 
         else:
            username_list.append(book.student.username)
      return HttpResponse(username_list, status= 201)


@csrf_exempt
def user_data_updated(request):
   id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   if not claims:
      return HttpResponse('Unauthorized')
   
   username = claims['firebase']['identities']['phone'][0][3:13]
   #username="1111111133"
   student = user_info.objects.get(username=username)
   name = student.firstname+ ' '+ student.lastname
   standard = student.standard

   goal = exam_info.objects.get(exam_id=standard)

   gender = student.gender
   photo = student.photo

   data = {
      "name": name,
      "standard": goal.exam_name,
      "gender": gender,
      "photo": photo
   }
   return JsonResponse(data, status= 201)

@csrf_exempt
def user_data(request):
   id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   if not claims:
      return HttpResponse('Unauthorized')
   #user_json_data=json.loads(request.body)
   #username = user_json_data['student'];
   username = claims['firebase']['identities']['phone'][0][3:13]

   student = user_info.objects.get(username=username)
   name = student.firstname+ ' '+ student.lastname
   standard = student.standard
   

   gender = student.gender
   photo = student.photo

   data = {
      "name": name,
      "standard": standard,
      "gender": gender,
      "photo": photo
   }
   return JsonResponse(data, status= 201)

@csrf_exempt
def check_if_user_exists(request):
   id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   if not claims:
      return HttpResponse('Unauthorized')
   
   username = claims['firebase']['identities']['phone'][0][3:13]
   #username = "1111111133"
   if(user_info.objects.filter(username=username).exists()):
      return JsonResponse({"status": True})

   return JsonResponse({"status": False})



@csrf_exempt
def getNameFromUsername(request):
   id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   if not claims:
      return HttpResponse('Unauthorized')
   #user_json_data=json.loads(request.body)
   #username = user_json_data['student'];
   username1 = claims['firebase']['identities']['phone']
   username = username1[0][3:13]

   student = user_info.objects.get(username=username)
   name = student.firstname+ ' ' + student.lastname
   return HttpResponse(name)


@csrf_exempt
def get_class_info(request):
   id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   if not claims:
      return HttpResponse('Unauthorized')


   exams = exam_info.objects.all().values_list('exam_id', 'exam_name', 'exam_type', flat=False)
   exam_list = []
   classes = []
   exam_preparation= []
   for exam in exams:
      if(exam[2] == 'Exam Preparation'):
         exam_data = {
            "id": exam[0],
            "name": exam[1],
         }
         exam_preparation.append(exam_data)
      elif(exam[2] == 'Classes 9 - 12+'):
         exam_data = {
            "id": exam[0],
            "name": exam[1],
         }
         classes.append(exam_data)
   array = []
   array.append({"Classes 9 - 12+": classes})
   array.append({"Exam Preparation": exam_preparation})
   return JsonResponse({"data": array})
   data = {
      "Classes 9 - 12+": classes,
      "Exam Preparation": exam_preparation
   }
   data1 = [{"Classes 9 - 12+": classes, "Exam Preparation": exam_preparation}]
   return JsonResponse({"data": data1})
        
   #return HttpResponse(exam_list[1]['type'])

   #groups = groupby(exam_list, lambda content: content['type'])
   #return HttpResponse(exam_list.groupby('type'))



@csrf_exempt
def update_parents_details(request):
   id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   if not claims:
      return HttpResponse('Unauthorized')
   user_json_data=json.loads(request.body)

   username = claims['firebase']['identities']['phone'][0][3:13]
   
   student_info = user_info.objects.get(username=username)

   try:
      if user_json_data['name'] is not None:
         name = user_json_data['name'];
   except Exception as e:
      pass;
   
   try:
      if user_json_data['relationship_to_student'] is not None:
         relationship_to_student = user_json_data['relationship_to_student'];
   except Exception as e:
      pass;
   
   try:
      if user_json_data['contact_number'] is not None:
         contact_number = user_json_data['contact_number'];
   except Exception as e:
      pass;
   
   chapter_object_object=parents_details(student=student_info, name = name, relationship_to_student=relationship_to_student, contact_number=contact_number)
   chapter_object_object.save()
   return JsonResponse({'status': 'True', 'message': 'Successfully updated'})
   

@csrf_exempt
def profile_progress(request):
   id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   if not claims:
      return HttpResponse('Unauthorized')

   username = claims['firebase']['identities']['phone'][0][3:13]
   #username = '1111111133'
   
   student_info = user_info.objects.get(username=username)
   
   progress=0.25

   if(student_info.photo != ''):
      detail_1 = True
      progress += 0.25
   else:
      detail_1 = False

   if(student_info.school != '' and student_info.coachings != ''):
      detail_2 = True
      progress += 0.25
   else:
      detail_2 = False   

   if parents_details.objects.filter(student__username=username).exists():
      detail_3 = True
      progress += 0.25
   else:
      detail_3 = False

   data = {
      "progress": progress,
      "profile_progress": [
      {
         "name": "profile_picture",
         "status": detail_1,
         "type": "state",
         "text": "Upload profile picture",
         "screen": "modalVisible"
      },
      {
         "name": "school_info",
         "status": detail_2,
         "type": "screen",
         "text": "Update Education details",
         "screen": "addDetails"
      },
      {
         "name": "parent_details",
         "status": detail_3,
         "type": "screen",
         "text": "Update parent details",
         "screen": "addParent"
      },
      ]
   }

   return HttpResponse(json.dumps(data), content_type='application/json')



@csrf_exempt
def announcements_updated(request):
   id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   if not claims:
      return HttpResponse('Unauthorized')
   
   username = claims['firebase']['identities']['phone'][0][3:13]
   #username = "1111111133"

   student = user_info.objects.get(username=username)
   standard = student.standard
   #return HttpResponse(student.standard)
   #username = '1111111122'
   myTeachersList = teacher_student_interaction.objects.filter(student__username = username, is_active = True).values_list('teacher__teacher_id', 'teacher__firstname', 'teacher__lastname', 'batch_id', 'teacher__photo', flat=False)

   #return HttpResponse(myTeachersList)
   arr=[]
   db = firestore.Client()
   for teacherIndex in range(len(myTeachersList)):
      docs = db.collection(u'announcement').document(myTeachersList[teacherIndex][0]).collection(myTeachersList[teacherIndex][3]).get()
      for doc in docs:
         a = doc.to_dict()

         if(a['type'] == 'deadline'):
            deadline_time = a['deadline_time']
            thumbnail = a['thumbnail']
            time_remaining= a['time_remaining']
         else:
            deadline_time = ""
            thumbnail = ""
            time_remaining = ""

         try:
            gender = a['gender']
         except:
            gender = 'male'


         try:
            if(int(standard) in a['class']):
               data = {
                  "firstname": myTeachersList[teacherIndex][1],
                  "lastname": myTeachersList[teacherIndex][2],
                  "gender": gender,
                  "photo": myTeachersList[teacherIndex][4],
                  "time": str(a['time']),
                  "message": a['message'],
                  "type": a['type'],
                  "action": a['action'],
                  "payload": a['payload'],
                  "deadline_time": deadline_time,
                  "thumbnail": thumbnail,
                  "time_remaining": time_remaining
               }
               arr.append(data)
         except:
            pass
   data = {
            "firstname": "Team ClassCast",
            "lastname": "",
            "gender": 'none',
            "photo": "https://storage.googleapis.com/classcast_images/ic_launcher_round.png",
            "time": '2019-08-08T14:09:41.500Z',
            "message": "Welcome to ClassCast",
            "type": "announcement",
            "action": "none",
            "payload": "none",
            "deadline_time": '',
            "thumbnail": '',
            "time_remaining": ''
         } 

   arr.append(data)

   data2 = {
            "firstname": "Team ClassCast",
            "lastname": "",
            "gender": 'none',
            "photo": "https://storage.googleapis.com/classcast_images/ic_launcher_round.png",
            "time": '2019-09-28T00:09:41.500Z',
            "message": "JEE main 2020 registration ends on September 30. Candidates can apply for the exam at the official website www.jeemain.nic.in.",
            "type": "announcement",
            "action": "weburl",
            "payload": "https://jeemain.nta.nic.in/webinfo/public/home.aspx",
            "thumbnail": '',
            "time_remaining": ''
         } 

   arr.append(data2)
   s = sorted(arr, key=lambda k: k.get('time', 0))
   return HttpResponse(json.dumps(s),  content_type="application/json")


@csrf_exempt
def createCourse(request):
   return HttpResponse('working')
   user_json_data=json.loads(request.body)

   return JsonResponse(user_json_data)


@csrf_exempt
def whatsnew(request):
   id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   if not claims:
      return HttpResponse('Unauthorized')
   
   #username = claims['firebase']['identities']['phone'][0][3:13]
   #username = "1111111133"

   arr=[]
   db = firestore.Client()
   docs = db.collection(u'whatsnewonclasscast').get()
   
   for doc in docs:
      json_data = doc.to_dict()

      if(json_data['active']):
         arr.append(json_data)

   s = sorted(arr, key=lambda k: k.get('time', 0), reverse=True)
   return HttpResponse(json.dumps(s),  content_type="application/json")


@csrf_exempt
def whatsnew_shyam_sharma(request):
   #id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   #claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   #if not claims:
   #   return HttpResponse('Unauthorized')
   
   #username = claims['firebase']['identities']['phone'][0][3:13]
   #username = "1111111133"

   arr=[]
   db = firestore.Client()
   docs = db.collection(u'whatsnew_shyamsharma').get()
   
   for doc in docs:
      json_data = doc.to_dict()

      if(json_data['active']):
         arr.append(json_data)

   s = sorted(arr, key=lambda k: k.get('time', 0), reverse=True)
   return HttpResponse(json.dumps(s),  content_type="application/json")

@csrf_exempt
def whatsnew_the_optimist(request):
   id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   if not claims:
      return HttpResponse('Unauthorized')
   
   #username = claims['firebase']['identities']['phone'][0][3:13]
   #username = "1111111133"

   arr=[]
   db = firestore.Client()
   docs = db.collection(u'whatsnew_the_optimist').get()
   
   for doc in docs:
      json_data = doc.to_dict()

      if(json_data['active']):
         arr.append(json_data)

   s = sorted(arr, key=lambda k: k.get('time', 0), reverse=True)
   return HttpResponse(json.dumps(s),  content_type="application/json")

@csrf_exempt
def whatsnew_spsharma(request):
   id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   if not claims:
      return HttpResponse('Unauthorized')
   
   #username = claims['firebase']['identities']['phone'][0][3:13]
   #username = "1111111133"

   arr=[]
   db = firestore.Client()
   docs = db.collection(u'whatsnew_spsharma').get()
   
   for doc in docs:
      json_data = doc.to_dict()

      if(json_data['active']):
         arr.append(json_data)

   s = sorted(arr, key=lambda k: k.get('time', 0), reverse=True)
   return HttpResponse(json.dumps(s),  content_type="application/json")

@csrf_exempt
def whatsnew_all(request, collection_name):
   #id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   #claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   #if not claims:
   #   return HttpResponse('Unauthorized')
   
   arr=[]
   db = firestore.Client()
   docs = db.collection(collection_name).get()
   
   for doc in docs:
      json_data = doc.to_dict()

      if(json_data['active']):
         arr.append(json_data)

   s = sorted(arr, key=lambda k: k.get('time', 0), reverse=True)
   return HttpResponse(json.dumps(s),  content_type="application/json")