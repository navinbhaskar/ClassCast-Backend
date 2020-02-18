from django.shortcuts import render
from rest_framework.views import APIView
from django.http import HttpResponse
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
import datetime
import sys
sys.path.append("..")
from mysite.users.models import user_info
from mysite.teachers.models import teacher_info, access_code, teacher_student_interaction, course_enrollment
import random
import string
import google.oauth2.id_token
import google.auth.transport.requests
import json

HTTP_REQUEST = google.auth.transport.requests.Request()



class generateAccessCode(APIView):
    def get(self, request, teacherid, batch_id, number):
        #id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        #claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        #if not claims:
        #    return HttpResponse('Unauthorized')
        token_list=[]
        batch_list=[]
        teacher_list=[]
        teacher=teacher_info.objects.get(teacher_id = teacherid)
        
        for i in range(int(number)):
            token = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            token_object=access_code(teacher=teacher, access_code = token, batch_id=batch_id, expired=False)
            token_object.save()
            token_list.append(token)
            batch_list.append(batch_id)
            teacher_list.append(teacher.firstname+ ' '+teacher.lastname)

        new_list = zip(teacher_list, batch_list, token_list)
        zipped = list(new_list)

        your_list_as_json = json.dumps(zipped)

        return HttpResponse(your_list_as_json, status=201 )
        #return Response('Updated', status= 201)
            
        
class enrollment_from_token(APIView):
    def post(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')
        username1 = claims['firebase']['identities']['phone']
        username = username1[0][3:13]
        #username='1111111122'
        data=request.data

        student=user_info.objects.get(username=username)
        try:
            access_code_object=access_code.objects.get(access_code=data['access_code'], expired=False)
            access_code_object.student = student
            access_code_object.expired = True
            access_code_object.save()
            teacher = access_code_object.teacher
            batch_id = access_code_object.batch_id
        except Exception as e:
            return Response('Invalid or Already Used', status=404)

        try:
            teacher_object=teacher_student_interaction(student=student, teacher=teacher, batch_id = batch_id, is_approved=True, is_active=True, date_joined=datetime.datetime.now())
            teacher_object.save()
            #this_batch=teacher_student_interaction.objects.get(student=student, teacher=teacher)
            #course = teacher.courses.split(',')
            #for course_id in course:
            #    if not course_id:
            #        pass;
            #    else:
            #        course_object = course_enrollment(student = student, course_id = course_id, batch = this_batch, date_joined = datetime.datetime.now())
            #        course_object.save()
            data = {
               "status": "OK",
               "batch_id": batch_id,
               "teacher": teacher.teacher_id,
               "teacher_firstname": teacher.firstname,
               "teacher_lastname": teacher.lastname,
               "teacher_coaching_name": teacher.coaching_name,
               "teacher_area": teacher.area,
               "teacher_subject": teacher.subject,
               "teacher_goal": teacher.goal,
               "teacher_courses": teacher.courses,
               "teacher_image": teacher.photo
            }
            return JsonResponse(data, status= 201)
        except Exception as e:

            return HttpResponse(e)

class enrollment_from_token_white_label(APIView):
    def post(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
       	if not claims:
            return HttpResponse('Unauthorized')
        username = claims['firebase']['identities']['phone'][0][3:13]
        #username='1111111133'
        data=request.data

        student=user_info.objects.get(username=username)
        try:
            access_code_object=access_code.objects.get(access_code=data['access_code'], expired=False)
            teacher = access_code_object.teacher
            if(teacher.teacher_id != data['teacher_id']):
              return Response('Invalid Code', status=404)  

            access_code_object.student = student
            access_code_object.expired = True
            access_code_object.save()
            batch_id = access_code_object.batch_id
        except Exception as e:
            return Response('Invalid or Already Used', status=404)

        try:
            teacher_object=teacher_student_interaction(student=student, teacher=teacher, batch_id = batch_id, is_approved=True, is_active=True, date_joined=datetime.datetime.now())
            teacher_object.save()
            
            data = {
               "status": "OK",
               "batch_id": batch_id,
               "teacher": data['teacher_id'],
               "teacher_firstname": teacher.firstname,
               "teacher_lastname": teacher.lastname,
               "teacher_coaching_name": teacher.coaching_name,
               "teacher_area": teacher.area,
               "teacher_subject": teacher.subject,
               "teacher_goal": teacher.goal,
               "teacher_courses": teacher.courses,
               "teacher_image": teacher.photo
            }
            return JsonResponse(data, status= 201)
        except Exception as e:

            return HttpResponse(e)



def access_code_data(request):
   #id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   #claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   #if not claims:
   #     return HttpResponse('Unauthorized')
   
   teacher_id=request.GET.get("teacher_id")
   #return HttpResponse(teacher_id)
   teacher=['Teacher Name']
   student_name=['Student Name']
   student_username=['Student Username']
   accessCode=['Access Code']
   if(teacher_id is not None):

        access_code_object=access_code.objects.filter(teacher__teacher_id= teacher_id, expired=True).values_list('teacher__firstname', 'teacher__lastname', 'access_code', 'student__firstname', 'student__lastname', 'student__username', flat=False)
        
        for i in range(len(access_code_object)):
            teacher.append(access_code_object[i][0]+' '+access_code_object[i][1])
            student_name.append(access_code_object[i][3]+' '+access_code_object[i][4])
            accessCode.append(access_code_object[i][2])
            student_username.append(access_code_object[i][5])

        new_list = zip(teacher, student_name, student_username, accessCode)
        zipped = list(new_list)

        your_list_as_json = json.dumps(zipped)

        return HttpResponse(your_list_as_json, status=201 )
   

   else:
        access_code_object=access_code.objects.filter(expired=True).values_list('teacher__firstname', 'teacher__lastname', 'access_code', 'student__firstname', 'student__lastname', 'student__username', flat=False)
        
        for i in range(len(access_code_object)):
            teacher.append(access_code_object[i][0]+' '+access_code_object[i][1])
            student_name.append(access_code_object[i][3]+' '+access_code_object[i][4])
            accessCode.append(access_code_object[i][2])
            student_username.append(access_code_object[i][5])

        new_list = zip(teacher, student_name, student_username, accessCode)
        zipped = list(new_list)

        your_list_as_json = json.dumps(zipped)

        return HttpResponse(your_list_as_json, status=201 )
   return HttpResponse('Something Went Wrong')
   #chapterList=request.GET.get("chapterList")
   #standard=request.GET.get("standard")