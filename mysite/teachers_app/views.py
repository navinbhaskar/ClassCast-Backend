from django.shortcuts import render
from rest_framework.views import APIView
from django.http import HttpResponse
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
import json
import datetime
from .models import teacher_account, teacher_batch_data, class_attendance_data, fcm_token_teacher, teacher_credentials
import sys
import random
import string
import uuid
sys.path.append("..")
from mysite.teachers.models import teacher_info, teacher_student_interaction, course_enrollment
from mysite.users.models import user_info, exam_info, parents_details
from mysite.course_data.models import student_block_interactions, exams, exams_package, test_sections, live_courses
from mysite.fcm_token.models import fcm_token
import google.oauth2.id_token
import google.auth.transport.requests
from firebase_admin import firestore, messaging
from django.core import serializers
from google.cloud.firestore_v1 import ArrayUnion, ArrayRemove
from django.views.decorators.csrf import csrf_exempt
from mysite.course_data.models import classcast_question, student_block_interactions, question, chapter_updated
import calendar

HTTP_REQUEST = google.auth.transport.requests.Request()


class teacher_data(APIView):
    def get(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')
        #username = 'Rohit1098'
        username = claims['email'].split('@')[0]
        teacher = teacher_account.objects.get(username = username)
        teacher_id = teacher.teacher.teacher_id
        name = teacher.teacher.firstname + ' ' + teacher.teacher.lastname
        subject = teacher.teacher.subject
        teacher_photo = teacher.teacher.photo
        coaching_name = teacher.teacher.coaching_name
        area = teacher.teacher.area
        courses = teacher.teacher.courses.split(',')
        batches = teacher.teacher.batches
        classcast_select = teacher.teacher.classcast_select

        student_count = teacher_student_interaction.objects.filter(teacher__teacher_id = teacher_id).count()

        data = {
            "username": username,
            "teacher_id": teacher_id,
            "name": name,
            "subject": subject,
            "photo": teacher_photo,
            "coaching_name": coaching_name,
            "area": area,
            "courses": len(courses),
            "classcast_select": classcast_select,
            "batches": len(batches),
            "student_count": student_count
        }
            #return HttpResponse(courseid)
        return Response(data)


class batch_list(APIView):
    def get(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')
        #username = 'Rohit1098'
        username = claims['email'].split('@')[0]

        teacher = teacher_account.objects.get(username = username)
        teacher_id = teacher.teacher.teacher_id
        batch_data=[]

        standard_list = teacher_batch_data.objects.filter(teacher__teacher_id = teacher_id).values_list('standard', 'batch_id',"sunday", 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'class_start_timing', 'class_end_timing', flat=False)
        for standard in standard_list:
            student_count = teacher_student_interaction.objects.filter(teacher__teacher_id = teacher_id, batch_id = standard[1], student__standard = standard[0]).count()
            goal = exam_info.objects.get(exam_id=standard[0])

            data = {
                "batch_id": standard[1],
                "goal": goal.exam_name,
                "standard": standard[0],
                "sunday": standard[2],
                "monday": standard[3],
                "tuesday": standard[4],
                "wednesday": standard[5],
                "thursday": standard[6],
                "friday": standard[7],
                "saturday": standard[8],
                "class_start_timing": standard[9],
                "class_end_timing": standard[10],
                "student_count": student_count
            }
            batch_data.append(data)
            #student_count = teacher_student_interaction.objects.filter(teacher__teacher_id = teacher_id, batch_id= batch)
        return Response(batch_data)


class all_student_list(APIView):
    def get(self, request, standard):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')
        #username = 'Rohit1098'
        username = claims['email'].split('@')[0]

        teacher = teacher_account.objects.get(username = username)
        teacher_id = teacher.teacher.teacher_id

        student_list=[]
        if(standard=='all'):
            student_dict = teacher_student_interaction.objects.filter(teacher__teacher_id = teacher_id).values_list('student__firstname', 'student__lastname', 'student__username', flat=False)
        else:
            student_dict = teacher_student_interaction.objects.filter(teacher__teacher_id = teacher_id, student__standard= standard).values_list('student__firstname', 'student__lastname', 'student__username', flat=False)

        for student in student_dict:
            data = {
                "name": student[0]+' '+student[1],
                "username": student[2]
            }
            student_list.append(data)

        return Response(student_list)


class student_list(APIView):
    def get(self, request, standard, batch_id):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')
        #username = 'Rohit1098'
        username = claims['email'].split('@')[0]

        teacher = teacher_account.objects.get(username = username)
        teacher_id = teacher.teacher.teacher_id

        student_list=[]

        student_dict = teacher_student_interaction.objects.filter(teacher__teacher_id = teacher_id, batch_id = batch_id, student__standard = standard).values_list('student__firstname', 'student__lastname', 'student__username', flat=False)
        for student in student_dict:
            data = {
                "name": student[0]+' '+student[1],
                "username": student[2]
            }
            student_list.append(data)

        return Response(student_list)

class submit_attendance(APIView):
    def post(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
          return HttpResponse('Unauthorized')

        username = claims['email'].split('@')[0]
        if(request.method == "GET"):
            return JsonResponse({'status': 'False', 'message': 'Get request'})

        teacher = teacher_account.objects.get(username = username)
        teacher_id = teacher.teacher.teacher_id
        user_json_data=json.loads(request.body)


        batch = teacher_batch_data.objects.get(teacher__teacher_id = teacher_id, batch_id = user_json_data['batch_id'], standard = user_json_data['standard'])

        for Object in user_json_data['students']:
            student = user_info.objects.get(username = Object['username'])
            if(class_attendance_data.objects.filter(student=student, batch=batch, timestamp = user_json_data['date']).exists()):
                class_attendance_data.objects.filter(student=student, batch=batch, timestamp = user_json_data['date']).update(class_attended=Object['class_attended'])
            else:
                class_attendance=class_attendance_data(student=student, batch=batch, class_attended=Object['class_attended'], timestamp=user_json_data['date'])
                class_attendance.save()
        #phonenumberList = user_json_data['number'];


        return Response(user_json_data)

class get_attendance_data(APIView):
    def post(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')

        user_json_data=json.loads(request.body)
        batch_id = user_json_data['batch_id']
        standard = user_json_data['standard']
        date = user_json_data['date']

        username = claims['email'].split('@')[0]
        #username = "pablo"

        teacher = teacher_account.objects.get(username = username)
        teacher_id = teacher.teacher.teacher_id

        batch = teacher_batch_data.objects.get(teacher__teacher_id = teacher_id, batch_id = batch_id, standard = standard)

        student_dict = teacher_student_interaction.objects.filter(teacher__teacher_id = teacher_id, batch_id = batch_id, student__standard = standard).values_list('student__firstname', 'student__lastname', 'student__username', flat=False)

        class_attendance=class_attendance_data.objects.filter(batch=batch, timestamp=date).values_list('student__firstname', 'student__lastname', 'student__username', 'class_attended', 'timestamp', flat=False)

        attendance_data = []

        for student in class_attendance:
            data = {
                "name": student[0]+' '+student[1],
                "username": student[2],
                "class_attended": student[3],
                "timestamp": student[4]
            }
            attendance_data.append(data)

        for student in student_dict:
            #[y[2] for y in class_attendance].index(i[2])
            try:
                temp = [y[2] for y in class_attendance].index(student[2])
            except:
                data = {
                    "name": student[0]+' '+student[1],
                    "username": student[2],
                    "class_attended": True,
                    "timestamp": ''
                }
                attendance_data.append(data)

        return Response(attendance_data)


class get_attendance_data_updated(APIView):
    def post(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')

        user_json_data=json.loads(request.body)
        batch_id = user_json_data['batch_id']
        standard = user_json_data['standard']
        date = user_json_data['date']

        username = claims['email'].split('@')[0]
        #username = "pablo"

        teacher = teacher_account.objects.get(username = username)
        teacher_id = teacher.teacher.teacher_id
        coaching_name = teacher.teacher.coaching_name

        batch = teacher_batch_data.objects.get(teacher__teacher_id = teacher_id, batch_id = batch_id, standard = standard)
        timings= batch.class_start_timing

        student_dict = teacher_student_interaction.objects.filter(teacher__teacher_id = teacher_id, batch_id = batch_id, student__standard = standard).values_list('student__firstname', 'student__lastname', 'student__username', flat=False)

        class_attendance=class_attendance_data.objects.filter(batch=batch, timestamp=date).values_list('student__firstname', 'student__lastname', 'student__username', 'class_attended', 'timestamp', flat=False)

        if(len(class_attendance)>0):
            attendance_taken = True
        else:
            attendance_taken = False

        attendance_data = []

        for student in class_attendance:
            phone_number = ''
            parents_details_exists = False
            try:
                parents_details_object = parents_details.objects.filter(student__username = student[2]).last()
                phone_number = parents_details_object.contact_number
                parents_details_exists= True
            except:
                pass

            data = {
                "name": student[0]+' '+student[1],
                "username": student[2],
                "class_attended": student[3],
                "timestamp": student[4],
                "parents_details_exists": parents_details_exists,
                "phone_number": phone_number
            }
            attendance_data.append(data)

        for student in student_dict:
            #[y[2] for y in class_attendance].index(i[2])
            try:
                temp = [y[2] for y in class_attendance].index(student[2])
            except:
                phone_number = ''
                parents_details_exists= False
                if(parents_details.objects.filter(student__username=student[2]).exists()):
                    parents_details_object = parents_details.objects.filter(student__username = student[2]).last()
                    phone_number = parents_details_object.contact_number
                    parents_details_exists= True

                data = {
                    "name": student[0]+' '+student[1],
                    "username": student[2],
                    "class_attended": True,
                    "timestamp": '',
                    "parents_details_exists": parents_details_exists,
                    "phone_number": phone_number
                }
                attendance_data.append(data)

        final_data={
        	"coaching_name": coaching_name,
        	"timings": timings,
            "attendance_taken_today": attendance_taken,
            "attendance_data": attendance_data
        }

        return Response(final_data)

class get_attendance_range_data(APIView):
    def post(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')
        #username='rohit1098'
        username = claims['email'].split('@')[0]

        user_json_data=json.loads(request.body)
        standard = user_json_data['standard']
        batch_id = user_json_data['batch_id']
        start_date = user_json_data['start_date']
        end_date = user_json_data['end_date']


        teacher = teacher_account.objects.get(username = username)
        teacher_id = teacher.teacher.teacher_id

        batch = teacher_batch_data.objects.get(teacher__teacher_id = teacher_id, batch_id = batch_id, standard = standard)
        student_dict = teacher_student_interaction.objects.filter(teacher__teacher_id = teacher_id, batch_id = batch_id, student__standard = standard).values_list('student__firstname', 'student__lastname', 'student__username', flat=False)


        class_attendance=class_attendance_data.objects.filter(batch=batch, timestamp__range=[start_date, end_date]).values_list('student__firstname', 'student__lastname', 'student__username', 'timestamp', 'class_attended', flat=False)
        #res_json = serializers.serialize('json', class_attendance.fields)
        #res_json = serializers.serialize('json', class_attendance)
        attendance_data = []
        total_classes = []
        no_class_attended = 0

        for student in class_attendance:
            if(student[3] not in total_classes):
                total_classes.append(student[3])

            if(student[4]):
                no_class_attended += 1

            data = {
                "name": student[0]+' '+student[1],
                "username": student[2],
                "class_attended": student[4]
            }
            attendance_data.append(data)

        for student in student_dict:
            #[y[2] for y in class_attendance].index(i[2])
            try:
                temp = [y[2] for y in class_attendance].index(student[2])
            except:
                data = {
                    "name": student[0]+' '+student[1],
                    "username": student[2],
                    "class_attended": False
                }
                attendance_data.append(data)
        if(len(class_attendance) != 0):
            percentage = (no_class_attended)* 100/len(class_attendance)
        else:
            percentage = 0

        data2 = {
            "total_classes": len(total_classes),
            "percentage": round(percentage),
            "student_data": attendance_data
        }

        return Response(data2)
        #return HttpResponse(class_attendance)
        #return JsonResponse(json.dumps(class_attendance))

class get_all_attendance_data(APIView):
    def post(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')

        username = claims['email'].split('@')[0]

        user_json_data=json.loads(request.body)
        standard = user_json_data['standard']
        batch_id = user_json_data['batch_id']

        teacher = teacher_account.objects.get(username = username)
        teacher_id = teacher.teacher.teacher_id

        batch = teacher_batch_data.objects.get(teacher__teacher_id = teacher_id, batch_id = batch_id, standard = standard)
        student_dict = teacher_student_interaction.objects.filter(teacher__teacher_id = teacher_id, batch_id = batch_id, student__standard = standard).values_list('student__firstname', 'student__lastname', 'student__username', flat=False)


        class_attendance=class_attendance_data.objects.filter(batch=batch).values_list('student__firstname', 'student__lastname', 'student__username', 'timestamp', 'class_attended', flat=False)
        #res_json = serializers.serialize('json', class_attendance.fields)
        #res_json = serializers.serialize('json', class_attendance)
        attendance_data = []

        for student in class_attendance:
            data = {
                "name": student[0]+' '+student[1],
                "username": student[2],
                "class_attended": student[3]
            }
            attendance_data.append(data)

        for student in student_dict:
            #[y[2] for y in class_attendance].index(i[2])
            try:
                temp = [y[2] for y in class_attendance].index(student[2])
            except:
                data = {
                    "name": student[0]+' '+student[1],
                    "username": student[2],
                    "class_attended": False
                }
                attendance_data.append(data)
        return Response(attendance_data)


class overview_attendance_data(APIView):
    def get(self, request, standard, batch_id):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')
        #username='rohit1098'
        username = claims['email'].split('@')[0]

        teacher = teacher_account.objects.get(username = username)
        teacher_id = teacher.teacher.teacher_id

        batch = teacher_batch_data.objects.get(teacher__teacher_id = teacher_id, batch_id = batch_id, standard = standard)
        student_dict = teacher_student_interaction.objects.filter(teacher__teacher_id = teacher_id, batch_id = batch_id, student__standard = standard).values_list('student__firstname', 'student__lastname', 'student__username', flat=False)


        class_attendance=class_attendance_data.objects.filter(batch=batch).values_list('student__firstname', 'student__lastname', 'student__username', 'timestamp', 'class_attended', flat=False)
        #res_json = serializers.serialize('json', class_attendance.fields)
        #res_json = serializers.serialize('json', class_attendance)
        attendance_data = []
        total_classes = []
        no_class_attended = 0

        for student in class_attendance:
            if(student[3] not in total_classes):
                total_classes.append(student[3])

            if(student[4]):
                no_class_attended += 1

            data = {
                "name": student[0]+' '+student[1],
                "username": student[2],
                "class_attended": student[4]
            }
            attendance_data.append(data)

        for student in student_dict:
            #[y[2] for y in class_attendance].index(i[2])
            try:
                temp = [y[2] for y in class_attendance].index(student[2])
            except:
                data = {
                    "name": student[0]+' '+student[1],
                    "username": student[2],
                    "class_attended": False
                }
                attendance_data.append(data)
        if(len(class_attendance) != 0):
            percentage = (no_class_attended)* 100/len(class_attendance)
        else:
            percentage = 0

        data2 = {
            "total_classes": len(total_classes),
            "percentage": round(percentage),
            "student_data": attendance_data
        }

        return Response(data2)

class batch_list_without_student_count(APIView):
    def get(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')
        #username = 'Rohit1098'
        username = claims['email'].split('@')[0]

        teacher = teacher_account.objects.get(username = username)
        teacher_id = teacher.teacher.teacher_id
        batches = teacher.teacher.batches.split(',')

        standard_list = teacher_batch_data.objects.filter(teacher__teacher_id = teacher_id)
        res_json = serializers.serialize('json', standard_list)

        return Response(json.loads(res_json))
        #return Response(standard_list)


class student_attendance_data(APIView):
    def get(self, request, student, standard, batch_id):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')
        #username='rohit1098'
        username = claims['email'].split('@')[0]

        teacher = teacher_account.objects.get(username = username)
        teacher_id = teacher.teacher.teacher_id

        batch = teacher_batch_data.objects.get(teacher__teacher_id = teacher_id, batch_id = batch_id, standard = standard)
        studentObject=user_info.objects.get(username=student)
        #return HttpResponse(student.firstname)
        class_attendance=class_attendance_data.objects.filter(student=studentObject, batch=batch)
        #for item in class_attendance:
        #    data={}
        res_json = serializers.serialize('json', class_attendance)
        data = {
            "name": studentObject.firstname+ ' '+studentObject.lastname,
            "gender": studentObject.gender,
            "standard": studentObject.standard,
            "phone": studentObject.phone_number,
            "photo": studentObject.photo,
            "attendance_data": json.loads(res_json)
        }
        return Response(data)
        #return HttpResponse(class_attendance)

class chat_data(APIView):
    def get(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')
        #username='rohit1098'
        username = claims['email'].split('@')[0]
        #username = "anuragc"
        teacher = teacher_account.objects.get(username = username)
        teacher_id = teacher.teacher.teacher_id

        student_dict = teacher_student_interaction.objects.filter(teacher__teacher_id = teacher_id).values_list('student__firstname', 'student__lastname', 'student__username', 'student__standard', 'batch_id', flat=False)

        db = firestore.Client()
        #
        doc_ref = db.collection(u'chatLists').document(username)
        doc = doc_ref.get()
        allCourseBlocks = doc.to_dict()
        batch_list=[]
        student_list = []
        try:
            for item in allCourseBlocks['chats']:
                if(item['type']=='student'):
                    if(item['isActive']):
                        student_list.append(item['username'])

                if(item['type']=='group'):
                    if(item['isActive']):
                        data={
                            "batch_id": item['display_name'],
                            "standard": str(item['display_extra_info']['class'])
                        }
                        batch_list.append(data)
        except:
            pass;
                #return HttpResponse(item['users'], content_type='application/json')
            #return HttpResponse(json.dumps(item), content_type='application/json')
        available_for_chat=[]



        standard_list = teacher_batch_data.objects.filter(teacher__teacher_id = teacher_id).values_list('standard', 'batch_id', flat=False)
        for standard in standard_list:
            student_count = teacher_student_interaction.objects.filter(teacher__teacher_id = teacher_id, batch_id = standard[1], student__standard = standard[0]).count()

            data = {
                "batch_id": standard[1],
                "standard": standard[0],
                "student_count": student_count,
                "type": "batch"
            }

            data2 = {
                "batch_id": standard[1],
                "standard": standard[0]
            }


            if(student_count > 0 and (data2 not in batch_list)):
                available_for_chat.append(data)


        for tc_interaction in student_dict:
            if(tc_interaction[2] not in student_list):
                data = {
                    "name": tc_interaction[0]+ ' '+ tc_interaction[1],
                    "username": tc_interaction[2],
                    "standard": tc_interaction[3],
                    "batch_id": tc_interaction[4],
                    "type": "student"
                }
                available_for_chat.append(data)

        return Response(available_for_chat)
        #return HttpResponse(json.dumps(allCourseBlocks['chats']), content_type='application/json')

class chat_data_student(APIView):
    def get(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')
        #username='rohit1098'
        available_for_chat=[]
        username = claims['firebase']['identities']['phone'][0][3:13]
        studentObject = user_info.objects.get(username = username)
        #username = "anuragc"
        #teacher = teacher_account.objects.get(username = username)
        #teacher_id = teacher.teacher.teacher_id

        teacher_dict = teacher_student_interaction.objects.filter(student__username = username).values_list('student__standard', 'batch_id', 'teacher__teacher_id', 'teacher__firstname', 'teacher__lastname', flat=False)
        #all_students=[]
        all_batch=[]
        full_student_list1 = []
        for teacher in teacher_dict:
            data = {
                "teacher_name": teacher[3] + ' '+ teacher[4],
                "teacher": teacher[2],
                "standard": teacher[0],
                "type": "teacher"
            }

            available_for_chat.append(data)

            student_list_batchwise = teacher_student_interaction.objects.filter(teacher__teacher_id = teacher[2], student__standard = teacher[0], batch_id = teacher[1]).values_list('student__firstname', 'student__lastname', 'student__username', 'student__username', flat=False)
            for item in student_list_batchwise:
                full_student_list1.append(item)

            #for student in full_student_list:
            #    all_students.append(student[2])
        full_student_list = list(dict.fromkeys(full_student_list1))

        db = firestore.Client()
        #
        doc_ref = db.collection(u'chatLists').document(username)
        doc = doc_ref.get()
        allCourseBlocks = doc.to_dict()
        batch_list=[]
        student_list = []
        try:
            for item in allCourseBlocks['chats']:
                if(item['isActive']):
                    if(item['type']=='student'):
                        student_list.append(item['username'])

                    if(item['type']=='group'):
                        data={
                            "teacher_id": item['teacher_id'],
                            "batch_id": item['display_name'],
                            "standard": str(item['display_extra_info']['class'])
                        }
                        batch_list.append(data)
        except:
            pass;


        for batch in teacher_dict:
            data2 = {
                "teacher_id": batch[2],
                "batch_id": batch[1],
                "standard": batch[0]
            }
            if(data2 not in batch_list):
                data = {
                    "batch_id": batch[1],
                    "standard": batch[0],
                    "teacher": batch[3]+ ' ' + batch[4],
                    "teacher_id": batch[2],
                    "type": "batch"
                }
                available_for_chat.append(data)


        for student in full_student_list:
            if(student[2] not in student_list):
                data = {
                    "name": student[0]+ ' '+ student[1],
                    "username": student[2],
                    "standard": studentObject.standard,
                    "type": "student"
                }
                available_for_chat.append(data)

        return Response(available_for_chat)



class add_batch(APIView):
    def post(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')
        #username = 'Rohit1098'
        username = claims['email'].split('@')[0]
        teacher = teacher_account.objects.get(username = username)
        teacher_id = teacher.teacher.teacher_id

        user_json_data=json.loads(request.body)
        standard = user_json_data['standard']
        batch_id = user_json_data['batch_id']

        try:
            sunday = user_json_data['sunday']
            monday = user_json_data['monday']
            tuesday = user_json_data['tuesday']
            wednesday = user_json_data['wednesday']
            thursday = user_json_data['thursday']
            friday = user_json_data['friday']
            saturday = user_json_data['saturday']
        except:
            sunday = False
            monday = False
            tuesday = False
            wednesday = False
            thursday = False
            friday = False
            saturday= False
        try:
            class_start_timing = user_json_data['class_start_timing']
            class_end_timing = user_json_data['class_end_timing']
        except:
            class_start_timing = datetime.time(00, 00)
            class_end_timing = datetime.time(00, 00)

        try:
            new_students = user_json_data['new_students']
        except:
            new_students = []

        teacher = teacher_account.objects.get(username = username)
        teacher_id = teacher.teacher.teacher_id

        teacher_info_data = teacher_info.objects.get(teacher_id = teacher_id)

        try:
            batch_data=teacher_batch_data(teacher=teacher_info_data, batch_id=batch_id, standard=standard, sunday = sunday, monday=monday, tuesday=tuesday, wednesday=wednesday, thursday=thursday, friday=friday, saturday=saturday, class_end_timing=class_end_timing, class_start_timing=class_start_timing)
            batch_data.save()

            for student_username in new_students:
                ts_interaction = teacher_student_interaction.objects.get(teacher__teacher_id = teacher_id, student__username = student_username)
                ts_interaction.batch_id = batch_id;
                ts_interaction.save()

            return JsonResponse({'status': 'True', 'message': 'Successfully updated'})
        except Exception as e:
            return HttpResponse(e)


class change_batch_data(APIView):
    def post(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')
        #username = 'pablo'
        username = claims['email'].split('@')[0]
        teacher = teacher_account.objects.get(username = username)
        teacher_id = teacher.teacher.teacher_id

        user_json_data=json.loads(request.body)
        standard = user_json_data['standard']
        batch_id = user_json_data['batch_id']

        try:
            sunday = user_json_data['sunday']
            monday = user_json_data['monday']
            tuesday = user_json_data['tuesday']
            wednesday = user_json_data['wednesday']
            thursday = user_json_data['thursday']
            friday = user_json_data['friday']
            saturday = user_json_data['saturday']
        except:
            sunday = False
            monday = False
            tuesday = False
            wednesday = False
            thursday = False
            friday = False
            saturday= False
        try:
            class_start_timing = user_json_data['class_start_timing']
            class_end_timing = user_json_data['class_end_timing']
        except:
            class_start_timing = datetime.time(00, 00)
            class_end_timing = datetime.time(00, 00)

        try:
            new_students = user_json_data['new_students']
        except:
            new_students = []


        teacher = teacher_account.objects.get(username = username)
        teacher_id = teacher.teacher.teacher_id
        teacher_info_data = teacher_info.objects.get(teacher_id = teacher_id)

        batch_info_data = teacher_batch_data.objects.get(teacher=teacher_info_data, batch_id=batch_id, standard=standard)
        batch_info_data.sunday = sunday
        batch_info_data.monday = monday
        batch_info_data.tuesday = tuesday
        batch_info_data.wednesday = wednesday
        batch_info_data.thursday = thursday
        batch_info_data.friday = friday
        batch_info_data.saturday = saturday
        batch_info_data.class_start_timing = class_start_timing
        batch_info_data.class_end_timing = class_end_timing

        batch_info_data.save()

        return HttpResponse('Updated')


class delete_batch(APIView):
    def post(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')
        #username = 'pablo'
        username = claims['email'].split('@')[0]
        teacher = teacher_account.objects.get(username = username)
        teacher_id = teacher.teacher.teacher_id

        user_json_data=json.loads(request.body)
        standard = user_json_data['standard']
        batch_id = user_json_data['batch_id']

        teacher = teacher_account.objects.get(username = username)
        teacher_id = teacher.teacher.teacher_id
        teacher_info_data = teacher_info.objects.get(teacher_id = teacher_id)

        batch_info_data = teacher_batch_data.objects.filter(teacher=teacher_info_data, batch_id=batch_id, standard=standard).delete()

        ts_interaction = teacher_student_interaction.objects.filter(teacher__teacher_id = teacher_id, batch_id = batch_id, student__standard = standard).delete()

        return HttpResponse('Deleted')



class available_batch(APIView):
    def get(self, request, batch_name, student_username):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')
        #username = 'Rohit1098'
        username = claims['email'].split('@')[0]

        teacher = teacher_account.objects.get(username = username)
        teacher_id = teacher.teacher.teacher_id

        user_info_object = user_info.objects.get(username = student_username)
        standard = user_info_object.standard

        batch_list = teacher_batch_data.objects.filter(teacher__teacher_id = teacher_id, standard = standard)

        res_json = serializers.serialize('json', batch_list)

        return Response(json.loads(res_json))


class chat_list(APIView):
    def get(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')
        #username='pablo'
        username = claims['email'].split('@')[0]

        teacher = teacher_account.objects.get(username = username)
        teacher_id = teacher.teacher.teacher_id

        db = firestore.Client()
        #
        doc_ref = db.collection(u'chatLists').document(username)
        try:
            doc = doc_ref.get()
            if(doc.to_dict() == None):
                doc_ref.set({
                    "chats": []
                })
                return Response([])
        except:
            pass


        doc = doc_ref.get()
        allCourseBlocks = doc.to_dict()

        chatLists=[]

        for entry in allCourseBlocks['chats']:
            if(entry['isActive']):
            #if(True):
                try:
                    if(entry['type'] == 'student'):
                        student_object = teacher_student_interaction.objects.get(teacher__teacher_id = teacher_id, student__username = entry['username'])
                        data = {
                            "chat_id": entry['chat_id'],
                            "username": entry['username'],
                            "name": entry['display_name'],
                            "standard": entry['display_extra_info']['class'],
                            "batch_id": student_object.batch_id,
                            "type": entry['type'],
                            "timestamp": entry['timestamp']
                        }

                    elif(entry['type'] == 'group'):
                        data = {
                            "chat_id": entry['chat_id'],
                            "standard": entry['display_extra_info']['class'],
                            "name": entry['display_name'],
                            "type": entry['type'],
                            "timestamp": entry['timestamp']
                        }
                    else:
                        pass

                    chatLists.append(data)
                except:
                    pass

        return Response(chatLists)


class chat_list_student(APIView):
    def get(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')
        #username='rohit1098'
        username = claims['firebase']['identities']['phone'][0][3:13]
        #username = '1111111122'

        db = firestore.Client()
        #
        doc_ref = db.collection(u'chatLists').document(username)

        try:
            doc = doc_ref.get()
            if(doc.to_dict() == None):
                doc_ref.set({
                    "chats": []
                })
                return Response([])
        except:
            pass

        allCourseBlocks = doc.to_dict()

        chatLists=[]

        for entry in allCourseBlocks['chats']:
            if(entry['isActive']):
            #if(True):
                if(entry['type'] == 'student'):
                    data = {
                        "chat_id": entry['chat_id'],
                        "username": entry['username'],
                        "name": entry['display_name'],
                        "standard": entry['display_extra_info']['class'],
                        "type": entry['type']
                    }
                elif(entry['type'] == 'teacher'):
                    data = {
                        "chat_id": entry['chat_id'],
                        "standard": entry['display_extra_info']['class'],
                        "name": entry['display_name'],
                        "type": entry['type']
                    }
                elif(entry['type'] == 'group'):
                    data = {
                        "chat_id": entry['chat_id'],
                        "teacher_name": entry['teacher_name'],
                        "standard": entry['display_extra_info']['class'],
                        "name": entry['display_name'],
                        "type": entry['type']
                    }
                else:
                    pass

                chatLists.append(data)
        return Response(chatLists)


class update_group_chat_data(APIView):
    def post(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')
        #username='rohit1098'
        username = claims['email'].split('@')[0]

        teacher = teacher_account.objects.get(username = username)
        teacher_firstname = teacher.teacher.firstname
        teacher_lastname = teacher.teacher.lastname
        teacher_id = teacher.teacher.teacher_id

        db = firestore.Client()

        user_json_data=json.loads(request.body)
        chat_id = user_json_data['chat_id']
        standard = user_json_data['standard']
        batch_id = user_json_data['batch_id']

        this_dict = {
            "chat_id": chat_id,
            "display_name": batch_id,
            "type": "group",
            "username": username,
            "teacher_name": teacher_firstname + ' ' + teacher_lastname,
            "display_extra_info": {
                "class": standard
            },
            "isActive": True
        }


        student_list_object = teacher_student_interaction.objects.filter(teacher__teacher_id = teacher_id, student__standard = standard, batch_id = batch_id).values_list('student__username', flat=True)

        for student_username in student_list_object:

            doc_ref = db.collection(u'chatLists').document(student_username)

            try:
                doc = doc_ref.get()
                if(doc.to_dict() == None):
                    doc_ref.set({
                        "chats": []
                    })
            except:
                pass

            doc_ref.update({
              "chats": ArrayUnion([this_dict])
            });

        return HttpResponse('Updated')


class update_group_chat_data_student(APIView):
    def post(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')
        #username='rohit1098'
        username = claims['firebase']['identities']['phone'][0][3:13]

        user_json_data=json.loads(request.body)
        chat_id = user_json_data['chat_id']
        standard = user_json_data['standard']
        batch_id = user_json_data['batch_id']
        teacher_id = user_json_data['teacher_id']
        teacher_name = user_json_data['teacher_name']

        db = firestore.Client()

        this_dict = {
            "chat_id": chat_id,
            "display_name": batch_id,
            "type": "group",
            "teacher_name": teacher_name,
            "display_extra_info": {
                "class": standard
            },
            "isActive": True
        }


        student_list_object = teacher_student_interaction.objects.filter(teacher__teacher_id = teacher_id, student__standard = standard, batch_id = batch_id).values_list('student__username', flat=True)

        for student_username in student_list_object:
            if(student_username != username):
                doc_ref = db.collection(u'chatLists').document(student_username)

                try:
                    doc = doc_ref.get()
                    if(doc.to_dict() == None):
                        doc_ref.set({
                            "chats": []
                        })
                except:
                    pass

                doc_ref.update({
                  "chats": ArrayUnion([this_dict])
                });

        return HttpResponse('Updated')



class store_chat_list_data(APIView):
    def post(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')
        #username='rohit1098'
        username = claims['email'].split('@')[0]

        teacher = teacher_account.objects.get(username = username)
        teacher_firstname = teacher.teacher.firstname
        teacher_lastname = teacher.teacher.lastname

        db = firestore.Client()

        user_json_data=json.loads(request.body)
        user_type = user_json_data['type']
        if(user_type == 'student'):
            display_name = user_json_data['display_name']
            student_username = user_json_data['username']
            standard = user_json_data['standard']
            chat_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

            this_dict = {
                "chat_id": chat_id,
                "display_name": display_name,
                "username": student_username,
                "type": user_type,
                "display_extra_info": {
                    "class": standard
                },
                "isActive": False
            }

            this_dict_student = {
                "chat_id": chat_id,
                "display_name": teacher_firstname+ ' ' +teacher_lastname,
                "username": username,
                "type": 'teacher',
                "display_extra_info": {
                    "class": standard
                },
                "isActive": False
            }

            doc_ref = db.collection(u'chatLists').document(username)
            doc = doc_ref.get()
            existing1 = False
            try:
                if(doc.to_dict() == None):
                    doc_ref.set({
                        "chats": []
                    })
                else:
                    allCourseBlocks = doc.to_dict()
                    for block in allCourseBlocks['chats']:
                        if(block['type'] == 'student'):
                            if(block['username']==student_username):
                                this_dict['chat_id'] = block['chat_id']
                                this_dict_student['chat_id'] = block['chat_id']
                                existing1 = True
            except:
                pass


            doc_ref2 = db.collection(u'chatLists').document(student_username)
            doc = doc_ref2.get()
            existing = False
            try:
                if(doc.to_dict() == None):
                    doc_ref2.set({
                        "chats": []
                    })
                else:
                    allCourseBlocks = doc.to_dict()
                    for block in allCourseBlocks['chats']:
                        if(block['type'] == 'teacher'):
                            if(block['username']==username):
                                this_dict['chat_id'] = block['chat_id']
                                this_dict_student['chat_id'] = block['chat_id']
                                existing = True
            except:
                pass

            if(existing == False):
                doc_ref2.update({
                  "chats": ArrayUnion([this_dict_student])
                });

            if(existing1 == False):
                doc_ref.update({
                  "chats": ArrayUnion([this_dict])
                });


        elif(user_type == 'group'):
            display_name = user_json_data['display_name']
            standard = user_json_data['standard']

            this_dict = {
                "chat_id": ''.join(random.choices(string.ascii_uppercase + string.digits, k=8)),
                "display_name": display_name,
                "type": user_type,
                "display_extra_info": {
                    "class": standard
                },
                "isActive": True
            }

            doc_ref = db.collection(u'chatLists').document(username)
            try:
                doc = doc_ref.get()
                if(doc.to_dict() == None):
                    doc_ref.set({
                        "chats": []
                    })
            except:
                pass

            doc_ref.update({
              "chats": ArrayUnion([this_dict])
            });

        return JsonResponse(this_dict)


class store_chat_list_data_student(APIView):
    def post(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')

        user_json_data=json.loads(request.body)

        username = claims['firebase']['identities']['phone'][0][3:13]
        #username = "1111111133"

        studentObject=user_info.objects.get(username=username)
        display_name = studentObject.firstname + ' ' + studentObject.lastname
        #teacher = teacher_info.objects.get(teacher_id = user_json_data['teacher_id'])
        #teacher_firstname = teacher.firstname
        #teacher_lastname = teacher.lastname


        db = firestore.Client()

        user_type = user_json_data['type']
        if(user_type == 'student'):
            student_display_name = user_json_data['display_name']
            student_username = user_json_data['username']
            standard = user_json_data['standard']
            chat_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            this_dict = {
                "chat_id": chat_id,
                "display_name": student_display_name,
                "username": student_username,
                "type": "student",
                "display_extra_info": {
                    "class": standard
                },
                "isActive": False
            }

            this_dict_student = {
                "chat_id": chat_id,
                "display_name": display_name,
                "username": username,
                "type": "student",
                "display_extra_info": {
                    "class": standard
                },
                "isActive": False
            }
            doc_ref = db.collection(u'chatLists').document(username)
            doc = doc_ref.get()
            existing = False
            try:
                if(doc.to_dict() == None):
                    doc_ref.set({
                        "chats": [],
                        "new_messages": False
                    })
                else:
                    allCourseBlocks = doc.to_dict()
                    for block in allCourseBlocks['chats']:
                        if(block['type'] == 'student'):
                            if(block['username']==student_username):
                                this_dict['chat_id'] = block['chat_id']
                                existing = True
            except:
                pass

            if(existing == False):
                doc_ref.update({
                  "chats": ArrayUnion([this_dict])
                });

            doc_ref2 = db.collection(u'chatLists').document(student_username)
            doc2 = doc_ref2.get()
            existing1 = False
            try:
                if(doc2.to_dict() == None):
                    doc_ref2.set({
                        "chats": [],
                        "new_messages": False
                    })
                else:
                    allCourseBlocks = doc2.to_dict()
                    for block in allCourseBlocks['chats']:
                        if(block['type'] == 'student'):
                            if(block['username']==username):
                                existing1 = True
            except:
                return JsonResponse(doc)
            if(existing1 == False):
                doc_ref2.update({
                  "chats": ArrayUnion([this_dict_student])
                });

            return JsonResponse(this_dict)

        elif(user_type == 'teacher'):
            teacher_display_name = user_json_data['teacher_name']
            teacher_id = user_json_data['teacher_id']
            standard = user_json_data['standard']

            teacher_object = teacher_account.objects.get(teacher__teacher_id = teacher_id)
            teacher_username = teacher_object.username.lower()

            chat_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            this_dict = {
                "chat_id": chat_id,
                "display_name": teacher_display_name,
                "username": teacher_username,
                "type": "teacher",
                "display_extra_info": {
                    "class": standard
                },
                "isActive": False
            }

            this_dict_student = {
                "chat_id": chat_id,
                "display_name": display_name,
                "username": username,
                "type": "student",
                "display_extra_info": {
                    "class": standard
                },
                "isActive": False
            }
            doc_ref = db.collection(u'chatLists').document(username)
            doc = doc_ref.get()
            existing = False
            try:
                if(doc.to_dict() == None):
                    doc_ref.set({
                        "chats": [],
                        "new_messages": False
                    })
                else:
                    allCourseBlocks = doc.to_dict()
                    for block in allCourseBlocks['chats']:
                        if(block['type'] == 'teacher'):
                            if(block['username']==teacher_username):
                                this_dict['chat_id'] = block['chat_id']
                                existing = True
            except:
                pass

            if(existing == False):
                doc_ref.update({
                  "chats": ArrayUnion([this_dict])
                });

            doc_ref2 = db.collection(u'chatLists').document(teacher_username)
            doc2 = doc_ref2.get()
            existing1 = False
            try:
                if(doc2.to_dict() == None):
                    doc_ref2.set({
                        "chats": []
                    })
                else:
                    allCourseBlocks = doc2.to_dict()
                    for block in allCourseBlocks['chats']:
                        if(block['type'] == 'student'):
                            if(block['username']==username):
                                existing1 = True
            except:
                return JsonResponse(doc)
            if(existing1 == False):
                doc_ref2.update({
                  "chats": ArrayUnion([this_dict_student])
                });

            return JsonResponse(this_dict)


        elif(user_type == 'group'):
            display_name = user_json_data['display_name']
            standard = user_json_data['standard']
            teacher_id = user_json_data['teacher_id']
            teacher_name = user_json_data['teacher_name']
            chat_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

            teacher_object = teacher_account.objects.get(teacher__teacher_id = user_json_data['teacher_id'])
            teacher_username = teacher_object.username.lower()

            doc_ref2 = db.collection(u'chatLists').document(teacher_username)
            doc = doc_ref2.get()
            existing = False
            try:
                if(doc.to_dict() == None):
                    doc_ref2.set({
                        "chats": []
                    })
                else:
                    allCourseBlocks = doc.to_dict()
                    for block in allCourseBlocks['chats']:
                        if(block['type']=='group'):
                            #return HttpResponse(block['display_extra_info']['class'])
                            if(block['display_name'] == display_name):
                                if(block['display_extra_info']['class'] == standard):
                                    existing= True
                                    chat_id = block['chat_id']
                                    pass
            except:
                return JsonResponse(doc)


            this_dict1 = {
                "chat_id": chat_id,
                "display_name": display_name,
                "teacher_id": teacher_id,
                "teacher_name": teacher_name,
                "type": user_type,
                "display_extra_info": {
                    "class": standard
                },
                "isActive": True
            }

            this_dict_batch = {
                "chat_id": chat_id,
                "display_name": display_name,
                "type": user_type,
                "display_extra_info": {
                    "class": standard
                },
                "isActive": True
            }

            doc_ref = db.collection(u'chatLists').document(username)
            try:
                doc = doc_ref.get()
                if(doc.to_dict() == None):
                    doc_ref.set({
                        "chats": []
                    })
            except:
                pass

            doc_ref.update({
              "chats": ArrayUnion([this_dict1])
            });

            if(existing==False):
                doc_ref2.update({
                  "chats": ArrayUnion([this_dict_batch])
                });

            return JsonResponse(this_dict1)

        return JsonResponse({ 'status': False })

class start_chat(APIView):
    def post(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')
        #username='rohit1098'
        try:
            username = claims['email'].split('@')[0]
        except:
            username = claims['firebase']['identities']['phone'][0][3:13]

        #teacher = teacher_account.objects.get(username = username)
        #teacher_id = teacher.teacher.teacher_id
        user_json_data=json.loads(request.body)
        chat_id = user_json_data['chat_id']

        this_dict = {
            "creatd": datetime.datetime.today(),
            "messages": []
        }

        db = firestore.Client()
        doc_ref = db.collection(u'chats').document(chat_id)
        doc = doc_ref.get()

        try:
            if(doc.to_dict() == None):
                doc_ref.set(this_dict)
        except:
            pass

        return JsonResponse(this_dict)

class update_chat_list(APIView):
    def post(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')
        #username='pablo'
        try:
            username = claims['email'].split('@')[0]
        except:
            username = claims['firebase']['identities']['phone'][0][3:13]

        user_json_data=json.loads(request.body)
        chat_id = user_json_data['chat_id']

        db = firestore.Client()
        doc_ref = db.collection(u'chatLists').document(username)
        doc = doc_ref.get()
        allCourseBlocks = doc.to_dict()
        #temp=[]
        Type = 'other'
        for item in allCourseBlocks['chats']:

            if(item['chat_id'] == chat_id):
                Type = item['type']
                chatListData = item
                doc_ref.update({
                  "chats": ArrayRemove([item])
                });

                item['isActive'] = True
                item['timestamp'] = '{0:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())

                doc_ref.update({
                  "chats": ArrayUnion([item])
                });

                break

        if(Type != 'group'):
            student_username = chatListData['username']
            doc_ref2 = db.collection(u'chatLists').document(student_username)
            doc2 = doc_ref2.get()
            allCourseBlocks = doc2.to_dict()
            #temp=[]
            for item in allCourseBlocks['chats']:

                if(item['chat_id'] == chat_id):


                    doc_ref2.update({
                      "chats": ArrayRemove([item])
                    });

                    item['isActive'] = True
                    item['timestamp'] = '{0:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())

                    doc_ref2.update({
                      "chats": ArrayUnion([item])
                    });

                    if(allCourseBlocks['new_messages']==False):
                        doc_ref2.update({
                          "new_messages": True
                        });

                        fcm_token_to = fcm_token.objects.get(student__username = student_username)

                        notification = messaging.Notification(title="ClassCast", body="You have a new message")
                        msg = messaging.Message(token=fcm_token_to.fcmToken,
                                                    notification = notification,
                                                    data={'title': "title", 'body': "message"})
                        msg_ = messaging.send(msg)



                    return HttpResponse('Updated')
                    break

        else:
            teacher_object = teacher_account.objects.select_related('teacher').get(username = username)
            teacher_id = teacher_object.teacher.teacher_id
            student_list_object = teacher_student_interaction.objects.filter(teacher__teacher_id = teacher_id, student__standard = chatListData['display_extra_info']['class'], batch_id = chatListData['display_name']).values_list('student__username', flat=True)
            fcm_token_to_list = fcm_token.objects.filter(student__username__in = student_list_object).values_list('student__username', 'fcmToken', flat=False)

            for fcm_token_dict in fcm_token_to_list:

                doc_ref3 = db.collection(u'chatLists').document(fcm_token_dict[0])
                doc2 = doc_ref3.get()
                allCourseBlocks = doc2.to_dict()

                if(allCourseBlocks['new_messages']==False):
                    if(username != fcm_token_dict[0]):
                        fcm_token_to = fcm_token_dict[1]
                        try:
                            notification = messaging.Notification(title="ClassCast", body="You have a new message")
                            msg = messaging.Message(token=fcm_token_to,
                                                        notification = notification,
                                                        data={'title': "title", 'body': "message"})
                            msg_ = messaging.send(msg)
                        except:
                            pass


                for item in allCourseBlocks['chats']:

                    if(item['chat_id'] == chat_id):
                        doc_ref3.update({
                          "chats": ArrayRemove([item])
                        });

                        item['isActive'] = True
                        item['timestamp'] = '{0:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())

                        doc_ref3.update({
                          "chats": ArrayUnion([item])
                        });
                        if(allCourseBlocks['new_messages']==False):
                            doc_ref3.update({
                              "new_messages": True
                            });

                        break


            return HttpResponse('Updated')
        #return HttpResponse(temp)
        return HttpResponse('Something Went Wrong')

class update_chat_list_student(APIView):
    def post(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')
        #username='rohit1098'

        username = claims['firebase']['identities']['phone'][0][3:13]

        #teacher = teacher_account.objects.get(username = username)
        #teacher_id = teacher.teacher.teacher_id
        user_json_data=json.loads(request.body)
        chat_id = user_json_data['chat_id']


        db = firestore.Client()

        doc_ref = db.collection(u'chatLists').document(username)
        doc = doc_ref.get()
        allCourseBlocks = doc.to_dict()

        chatListData = []

        for item in allCourseBlocks['chats']:
            #temp.append(item['chat_id'])
            #temp.append("||")
            if(item['chat_id'] == chat_id):
                chatListData = item

                doc_ref.update({
                  "chats": ArrayRemove([item])
                });

                item['isActive'] = True
                item['timestamp'] = '{0:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())

                doc_ref.update({
                  "chats": ArrayUnion([item])
                });

                break

        if(chatListData['type'] == 'student'):
            doc_ref2 = db.collection(u'chatLists').document(chatListData['username'])
            doc2 = doc_ref2.get()

            try:
                if(doc2.to_dict() == None):
                    doc_ref2.set({
                        "chats": [],
                        "new_messages": True
                    })
            except:
                pass


            allCourseBlocks = doc2.to_dict()

            if(allCourseBlocks['new_messages']==False):

                doc_ref2.update({
                      "new_messages": True
                    });
                fcm_token_to = fcm_token.objects.get(student__username = chatListData['username'])

                notification = messaging.Notification(title="ClassCast", body="You have a new message")
                msg = messaging.Message(token=fcm_token_to.fcmToken,
                                            notification = notification,
                                            data={'title': "title", 'body': "message"},
                                            android = messaging.AndroidConfig(priority= 'high', notification = messaging.AndroidNotification(sound='default', icon='ic_launcher')),

                                            )
                msg_ = messaging.send(msg)


            #temp=[]
            for item in allCourseBlocks['chats']:
                #temp.append(item['chat_id'])
                #temp.append("||")
                if(item['chat_id'] == chat_id):


                    doc_ref2.update({
                      "chats": ArrayRemove([item])
                    });

                    item['isActive'] = True
                    item['timestamp'] = '{0:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())

                    doc_ref2.update({
                      "chats": ArrayUnion([item])
                    });
                    return HttpResponse('Updated')
                    break



        if(chatListData['type'] == 'teacher'):
            doc_ref2 = db.collection(u'chatLists').document(chatListData['username'])
            doc2 = doc_ref2.get()
            allCourseBlocks = doc2.to_dict()


            if(allCourseBlocks['new_messages']==False):
                doc_ref2.update({
                      "new_messages": True
                    });
                fcm_token_to = fcm_token_teacher.objects.get(teacher__username = chatListData['username'])

                notification = messaging.Notification(title="ClassCast", body="You have a new message")
                msg = messaging.Message(token=fcm_token_to.fcmToken,
                                            notification = notification,
                                            data={'title': "title", 'body': "message"})
                msg_ = messaging.send(msg)

            #temp=[]
            for item in allCourseBlocks['chats']:
                #temp.append(item['chat_id'])
                #temp.append("||")
                if(item['chat_id'] == chat_id):


                    doc_ref2.update({
                      "chats": ArrayRemove([item])
                    });

                    item['isActive'] = True
                    item['timestamp'] = '{0:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())

                    doc_ref2.update({
                      "chats": ArrayUnion([item])
                    });
                    return HttpResponse('Updated')
                    break

        if(chatListData['type'] == 'group'):
            doc_ref2 = db.collection(u'chatLists').document(chatListData['username'])
            doc = doc_ref2.get()
            allCourseBlocks = doc.to_dict()

            for item in allCourseBlocks['chats']:

                if(item['chat_id'] == chat_id):
                    doc_ref2.update({
                      "chats": ArrayRemove([item])
                    });

                    item['isActive'] = True
                    item['timestamp'] = '{0:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())

                    doc_ref2.update({
                      "chats": ArrayUnion([item])
                    });

                    break



            teacher_object = teacher_account.objects.select_related('teacher').get(username = chatListData['username'])
            teacher_id = teacher_object.teacher.teacher_id


            if(allCourseBlocks['new_messages']==False):
                fcm_token_to = fcm_token_teacher.objects.get(teacher__username = chatListData['username'])

                notification = messaging.Notification(title="ClassCast", body="You have a new message")
                msg = messaging.Message(token=fcm_token_to.fcmToken,
                                            notification = notification,
                                            data={'title': "title", 'body': "message"})
                msg_ = messaging.send(msg)

            student_list_object = teacher_student_interaction.objects.filter(teacher__teacher_id = teacher_id, student__standard = chatListData['display_extra_info']['class'], batch_id = chatListData['display_name']).values_list('student__username', flat=True)
            fcm_token_to_list = fcm_token.objects.filter(student__username__in = student_list_object).values_list('student__username', 'fcmToken', flat=False)

            for fcm_token_dict in fcm_token_to_list:

                doc_ref3 = db.collection(u'chatLists').document(fcm_token_dict[0])
                doc2 = doc_ref3.get()
                allCourseBlocks = doc2.to_dict()

                if(allCourseBlocks['new_messages']==False):
                    if(username != fcm_token_dict[0]):
                        fcm_token_to = fcm_token_dict[1]

                        notification = messaging.Notification(title="ClassCast", body="You have a new message")
                        msg = messaging.Message(token=fcm_token_to,
                                                    notification = notification,
                                                    data={'title': "title", 'body': "message"})
                        msg_ = messaging.send(msg)


                for item in allCourseBlocks['chats']:

                    if(item['chat_id'] == chat_id):
                        doc_ref3.update({
                          "chats": ArrayRemove([item])
                        });

                        item['isActive'] = True
                        item['timestamp'] = '{0:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())

                        doc_ref3.update({
                          "chats": ArrayUnion([item])
                        });
                        doc_ref3.update({
                          "new_messages": True
                        });

                        break


            return HttpResponse('Updated')
        #return HttpResponse(temp)
        return HttpResponse('Something Went Wrong')


@csrf_exempt
def createprofile(request):
   id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   if not claims:
      return HttpResponse('Unauthorized')
   teacher_username = claims['email'].split('@')[0]
   #teacher_username = 'pablo'
   user_json_data=json.loads(request.body)
   username = user_json_data['username'];

   if user_info.objects.filter(username=username).exists():
        user_data = user_info.objects.get(username=username)
        return JsonResponse({'status': 'Used', 'name': user_data.firstname+ ' '+user_data.lastname, 'message': 'Phone number already used'})

   firstname = user_json_data['firstname'];
   lastname = user_json_data['lastname'];
   gender = user_json_data['gender'];
   standard = user_json_data['standard'];
   phone_number = user_json_data['phone_number'];
   email = user_json_data['email'];
   batch_id = user_json_data['batch_id']


   teacher = teacher_account.objects.get(username = teacher_username)
   teacher_id = teacher.teacher.teacher_id

   try:
        userData = user_info(firstname=firstname,
                       lastname=lastname,
                       gender=gender,
                       standard=standard,
                       phone_number=phone_number,
                       username=username,
                       email = email,
                       date_joined=datetime.datetime.today(),
                       )

        userData.save()

        student=user_info.objects.get(username=phone_number)
        teacher=teacher_info.objects.get(teacher_id = teacher_id)
        teacher_object=teacher_student_interaction(student=student, teacher=teacher, batch_id = batch_id, is_approved=True, is_active=True, date_joined=datetime.datetime.now())
        teacher_object.save()


        return JsonResponse({'status': 'True', 'message': 'Successfully created'})
   except Exception as e:
        return HttpResponse(e)


@csrf_exempt
def updateStudetProfile(request):
   id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
   claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
   if not claims:
      return HttpResponse('Unauthorized')
   #username='rohit1098'
   username = claims['email'].split('@')[0]

   teacher = teacher_account.objects.get(username = username)
   teacher_id = teacher.teacher.teacher_id

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
         if user_json_data['firstname'] is not None:
            student_info.firstname = user_json_data['firstname'];
      except Exception as e:
         pass;

      try:
         if user_json_data['lastname'] is not None:
            student_info.lastname = user_json_data['lastname'];
      except Exception as e:
         pass;

      try:
         if user_json_data['gender'] is not None:
            student_info.gender = user_json_data['gender'];
      except Exception as e:
         pass;

      try:
         if user_json_data['batch_id'] is not None:
            ts_interaction = teacher_student_interaction.objects.get(teacher__teacher_id = teacher_id, student__username = username)
            ts_interaction.batch_id = user_json_data['batch_id'];
            ts_interaction.save()

      except Exception as e:
         pass;

      try:
         if user_json_data['phone_number'] is not None:
            if user_info.objects.filter(phone_number=user_json_data[phone_number]).exists():
                return JsonResponse({'status': 'True', 'message': 'Phone number already used'})

            else:
                student_info.phone_number = user_json_data['phone_number'];
                student_info.username = user_json_data['phone_number'];
                student_info.email = user_json_data['phone_number']+'@gmail.com';
      except Exception as e:
         pass;
      student_info.save()
   return JsonResponse({'status': 'True', 'message': 'Successfully updated'})




class student_list_with_batch_id(APIView):
    def get(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')
        #username='pablo'
        username = claims['email'].split('@')[0]

        teacher = teacher_account.objects.get(username = username)
        teacher_id = teacher.teacher.teacher_id

        #batch_list = teacher_batch_data.objects.filter(teacher__teacher_id = teacher_id).values_list('standard','batch_id' ,flat=False)
        student_list=[]

        student_dict = teacher_student_interaction.objects.filter(teacher__teacher_id = teacher_id).values_list('student__firstname', 'student__lastname', 'student__username', 'student__standard', 'batch_id',flat=False)

        for student in student_dict:

            goal = exam_info.objects.get(exam_id=student[3])

            data = {
                "name": student[0]+' '+student[1],
                "username": student[2],
                "standard": student[3],
                "batch_id": student[4],
                "goal": goal.exam_name
            }
            student_list.append(data)

        return Response(student_list)


class edit_student_data(APIView):
    def get(self, request, student_username):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')
        #username = 'Rohit1098'
        username = claims['email'].split('@')[0]

        teacher = teacher_account.objects.get(username = username)
        teacher_id = teacher.teacher.teacher_id

        student = user_info.objects.get(username = student_username)

        if(student.gender == "1"):
            gender = "Male"
        elif(student.gender == "2"):
            gender = "Female"
        else:
            gender = student.gender

        ts_interaction = teacher_student_interaction.objects.get(teacher__teacher_id = teacher_id, student__username=student_username)

        data = {
            "firstname": student.firstname,
            "lastname": student.lastname,
            "gender": gender,
            "phone_number": student.phone_number,
            "standard": student.standard,
            "batch_id": ts_interaction.batch_id
        }

        return Response(data)


class get_batch_data(APIView):
    def get(self, request, standard, batch_id):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')
        #username='rohit1098'
        username = claims['email'].split('@')[0]

        teacher = teacher_account.objects.get(username = username)
        teacher_id = teacher.teacher.teacher_id

        batch = teacher_batch_data.objects.get(teacher__teacher_id = teacher_id, batch_id = batch_id, standard = standard)
        data = {
            "sunday" : batch.sunday,
            "monday" : batch.monday,
            "tuesday" : batch.tuesday,
            "wednesday" : batch.wednesday,
            "thursday" : batch.thursday,
            "friday" : batch.friday,
            "saturday" : batch.saturday,
            "class_start_timing" : batch.class_start_timing,
            "class_end_timing" : batch.class_end_timing
        }
        return Response(data)


class add_ts_interaction(APIView):
    @csrf_exempt
    def post(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')
        #username = 'pablo'
        username = claims['email'].split('@')[0]

        teacher = teacher_account.objects.get(username = username)
        teacher_id = teacher.teacher.teacher_id

        user_json_data=json.loads(request.body)
        student_username = user_json_data['username']
        batch_id = user_json_data['batch_id']

        teacher_info_data = teacher_info.objects.get(teacher_id = teacher_id)
        student_info_data = user_info.objects.get(username = student_username)

        teacher_student_interaction_object=teacher_student_interaction(teacher = teacher_info_data, student=student_info_data, batch_id=batch_id)
        teacher_student_interaction_object.save()

        return JsonResponse({'status': 'True', 'message': 'Successfully Added'})


class delete_ts_interaction(APIView):
    @csrf_exempt
    def post(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')
        #username = 'Rohit1098'
        username = claims['email'].split('@')[0]

        teacher = teacher_account.objects.get(username = username)
        teacher_id = teacher.teacher.teacher_id

        user_json_data=json.loads(request.body)
        username_list = user_json_data['username_list']
        if(teacher_student_interaction.objects.filter(teacher__teacher_id = teacher_id, student__username__in=username_list).count() < 20):
            ts_interaction = teacher_student_interaction.objects.filter(teacher__teacher_id = teacher_id, student__username__in=username_list).delete()
            return JsonResponse({'status': 'True', 'message': 'Successfully deleted'})
        return JsonResponse({'status': 'False', 'message': 'limit exceeded'})


class username_to_name(APIView):
    def get(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')

        username = claims['email'].split('@')[0]

        teacher = teacher_account.objects.get(username = username)
        teacher_firstname = teacher.teacher.firstname
        teacher_lastname = teacher.teacher.lastname
        name = teacher_firstname + ' ' + teacher_lastname

        return HttpResponse(name)


class updateMessageSeenStatus(APIView):
    def get(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')
        #username='rohit1098'
        try:
            username = claims['firebase']['identities']['phone'][0][3:13]
        except:
            username = claims['email'].split('@')[0]

        db = firestore.Client()
        doc_ref = db.collection(u'chatLists').document(username)

        try:
            doc = doc_ref.get()
            if(doc.to_dict() == None):
                doc_ref.set({
                    "chats": [],
                    "new_messages": False
                })
        except:
            pass


        doc_ref.update({
          "new_messages": False
        });

        return HttpResponse('Updated')


class save_fcm_token(APIView):
    def post(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')

        username = claims['email'].split('@')[0]

        data = request.data
        if fcm_token_teacher.objects.filter(teacher__username=username).exists():
            #return HttpResponse("working")
            fcm_token_teacher.objects.filter(teacher__username=username).update(fcmToken=data['fcmToken'])
            return Response('Updated', status= 201)
        else:
            y = fcm_token_teacher()
            y.teacher = teacher_account.objects.get(username=username)
            y.fcmToken = data['fcmToken']
            y.save()
            return Response('created', status= 201)

class get_fcm_token(APIView):
    def get(self, request, username):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')

        fcm = fcm_token_teacher.objects.get(teacher__username=username)
        return HttpResponse(fcm.fcmToken)


class announcement(APIView):
    def post(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
          return HttpResponse('Unauthorized')

        username = claims['email'].split('@')[0]
        #username = "pablo"
        if(request.method == "GET"):
            return JsonResponse({'status': 'False', 'message': 'Get request'})

        teacher = teacher_account.objects.get(username = username)
        teacher_id = teacher.teacher.teacher_id
        user_json_data=json.loads(request.body)

        standard = user_json_data['standard']
        batch_id = user_json_data['batch_id']
        message = user_json_data['message']
        payload = user_json_data['payload']
        action = user_json_data['action']
        date = user_json_data['date']

        doc_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

        data = {
            "action": action,
            "message": message,
            "class": standard,
            "time": date,
            "payload": payload,
            "type": "announcement"
        }

        db = firestore.Client()
        doc_ref = db.collection(u'announcement').document(str(teacher_id)).collection(batch_id).document(doc_id)

        doc_ref.set(data)

        return HttpResponse('Updated')


def exams_list(request):
    id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
    claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
    if not claims:
        return HttpResponse('Unauthorized')

    username = claims['email'].split('@')[0]
    #username = "pablo"

    teacher = teacher_account.objects.get(username = username)
    teacher_id = teacher.teacher.teacher_id

    batch = teacher_batch_data.objects.filter(teacher__teacher_id = teacher_id).values_list('standard', flat=True)

    b = list(batch)
    output = []
    for x in b:
        if x not in output:
            output.append(x)

    #return HttpResponse(output)

    final_data = []

    for standard in output:
        exams_object=exams.objects.filter(course__exam_id=standard)
        goal = exam_info.objects.get(exam_id=standard)

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

        data2 = {
            "goal": goal.exam_name,
            "standard": standard,
            "data": test_info
        }
        final_data.append(data2)



    return HttpResponse(json.dumps(final_data), content_type='application/json')


def availableClasses(request):
    id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
    claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
    if not claims:
        return HttpResponse('Unauthorized')

    username = claims['email'].split('@')[0]
    #username = "pablo"

    teacher = teacher_account.objects.get(username = username)
    teacher_id = teacher.teacher.teacher_id

    batch = teacher_batch_data.objects.filter(teacher__teacher_id = teacher_id).values_list('standard', flat=True)

    b = list(batch)
    output = []
    for x in b:
        if x not in output:
            output.append(x)

    #return HttpResponse(output)

    final_data = []

    for standard in output:
        exams_object=exams.objects.filter(course__exam_id=standard)
        goal = exam_info.objects.get(exam_id=standard)

        data = {
            "goal": goal.exam_name,
            "standard": standard
        }
        final_data.append(data)



    return HttpResponse(json.dumps(final_data), content_type='application/json')


@csrf_exempt
def get_test_data(request):
    id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
    claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
    if not claims:
      return HttpResponse('Unauthorized')

    username = claims['email'].split('@')[0]
    #username = "pablo"
    teacher = teacher_account.objects.get(username = username)
    teacher_id = teacher.teacher.teacher_id

    data=json.loads(request.body)
    standard = data['standard']

    #goal = exam_info.objects.get(exam_id=standard)
    #ssc
    #exams_object=exams.objects.filter(course__exam_id=standard)
    index = random.randint(1,100)

    package = data['exams_package']
    exam_name = data['exam_name']
    duration = data['duration']
    test_time = data['test_time']
    batch_id = data['batch_id']

    if(duration == 30):
      no_of_questions_per_section = 10
    else:
      no_of_questions_per_section = 20

    exam_package_object = exams_package.objects.get(section=package)
    #ssc_cpo
    sections = test_sections.objects.filter(exams_package = exam_package_object).values_list('section','section_name', flat=False)
    
    test_data = []
    db = firestore.Client()
    total_questions = 0

    for i in sections:
      quesList=[]
      
      doc_ref = db.collection(u'new_question_database').document(u'exams').collection(standard).document(exam_name).collection(package).where(u'section', u'==', i[0]).where(u'index', u'>=', index)
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
      total_questions += len(quesList)
       
    test_id = str(uuid.uuid4())

    final_data = {
        "test_id": test_id,
        "send_by": username,
        "class": standard,
        "send_by_id": teacher_id,
        "test_time": test_time,
        "package": package,
        "exam_name": exam_name,
        "duration": duration,
        "blocks": test_data,
        "participants": [],
        "performance": [],
        "batch_id": batch_id,
        "no_of_questions": total_questions
    }

    doc_ref = db.collection(u'test').document(test_id)
    doc_ref.set(final_data)

    return HttpResponse(json.dumps(test_data), content_type='application/json')


@csrf_exempt
def get_chapterwise_test_data(request):
    id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
    claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
    if not claims:
      return HttpResponse('Unauthorized')

    username = claims['email'].split('@')[0]
    #username = "pablo"
    teacher = teacher_account.objects.get(username = username)
    teacher_id = teacher.teacher.teacher_id

    data=json.loads(request.body)
    standard = data['standard']

    goal = exam_info.objects.get(exam_id=standard)
    #ssc
    #exams_object=exams.objects.filter(course__exam_id=standard)
    index = random.randint(1,100)

    package = data['exams_package']
    exam_name = data['exam_name']
    duration = data['duration']
    sections = data['chapters']
    test_time = data['test_time']
    batch_id = data['batch_id']

    if(duration == 30):
      no_of_questions_per_section = 10
    else:
      no_of_questions_per_section = 20

    #exam_package_object = exams_package.objects.get(section=package)
    #ssc_cpo
    #sections = test_sections.objects.filter(exams_package = exam_package_object).values_list('section','section_name', flat=False)

    test_data = []
    db = firestore.Client()
    total_questions = 0

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

      total_questions += len(quesList)


      test_data.append(
          {
            "section": i,
            "section_name": i,
            "data": quesList
          }
        )


    test_id = str(uuid.uuid4())

    final_data = {
        "test_id": test_id,
        "send_by": username,
        "class": standard,
        "send_by_id": teacher_id,
        "test_time": test_time,
        "package": package,
        "exam_name": exam_name,
        "duration": duration,
        "sections": sections,
        "blocks": test_data,
        "performance": [],
        "participants": [],
        "batch_id": batch_id,
        "no_of_questions": total_questions
    }

    doc_ref = db.collection(u'test').document(test_id)
    doc_ref.set(final_data)

    return HttpResponse(json.dumps(final_data), content_type='application/json')


@csrf_exempt
def get_topic_list(request):
    id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
    claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
    if not claims:
      return HttpResponse('Unauthorized')

    #student=user_info.objects.get(username=username)
    #standard = student.standard
    data=json.loads(request.body)

    standard = data['standard']
    goal = exam_info.objects.get(exam_id=standard)

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


class fetchTestData(APIView):
    def get(self, request, test_id):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')

        db = firestore.Client()

        doc_ref = db.collection(u'test').document(test_id)
        doc = doc_ref.get()
        allCourseBlocks = doc.to_dict()

        return JsonResponse(allCourseBlocks)


class storeTestPerformnce(APIView):
    def get(self, request, test_id, points):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')

        username = claims['firebase']['identities']['phone'][0][3:13]

        user_info_object = user_info.objects.get(username = username)

        firstname = user_info_object.firstname
        lastname = user_info_object.lastname

        db = firestore.Client()

        doc_ref = db.collection(u'test').document(test_id)

        data = {
            "name": firstname+' '+lastname,
            "username": username,
            "points": int(points)
        }
        doc_ref.update({u'performance': firestore.ArrayUnion([data])})

        return HttpResponse('Updated')

class newStoreTestPerformnce(APIView):
    def get(self, request, test_id, points, total):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')

        username = claims['firebase']['identities']['phone'][0][3:13]
        #username = "1111111133"

        user_info_object = user_info.objects.get(username = username)

        firstname = user_info_object.firstname
        lastname = user_info_object.lastname

        db = firestore.Client()

        doc_ref = db.collection(u'test').document(test_id)

        data = {
            "name": firstname+' '+lastname,
            "username": username,
            "points": int(points),
            "total": int(total)
        }
        doc_ref.update({u'performance': firestore.ArrayUnion([data])})

        doc_ref.update({u'participants': firestore.ArrayUnion([username])})

        return HttpResponse('Updated')


class sendTestToStudents(APIView):
    def post(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')

        username = claims['email'].split('@')[0]

        teacher = teacher_account.objects.get(username = username)
        teacher_id = teacher.teacher.teacher_id

        user_json_data=json.loads(request.body)

        image_index = random.randint(0,9)

        image_array = ['https://storage.googleapis.com/classcast_test_tiles/abstract-background-with-3d-lines_1361-1478.jpg',
                        'https://storage.googleapis.com/classcast_test_tiles/black-background-with-orange-hexagonal-pattern_1017-19746.jpg',
                        'https://storage.googleapis.com/classcast_test_tiles/blue-light-sparkles-background-with-copyspace_1017-20091.jpg',
                        'https://storage.googleapis.com/classcast_test_tiles/elegant-green-creative-lines-header-template-background_1035-16352.jpg',
                        'https://storage.googleapis.com/classcast_test_tiles/gradient-geometric-shape-background_78532-374.jpg',
                        'https://storage.googleapis.com/classcast_test_tiles/gradient-geometric-shape-background_78532-380.jpg',
                        'https://storage.googleapis.com/classcast_test_tiles/gradient-geometric-shapes-background_52683-12505.jpg',
                        'https://storage.googleapis.com/classcast_test_tiles/mandala-illustration_53876-75291.jpg',
                        'https://storage.googleapis.com/classcast_test_tiles/neon-lights-technology-geometric-background_52683-13534.jpg',
                        'https://storage.googleapis.com/classcast_test_tiles/technology-digital-data-mesh-network-background_1017-19691.jpg'
                        ]

        test_id = user_json_data['test_id']
        date = user_json_data['date']
        deadline = user_json_data['deadline']
        standard = user_json_data['standard']
        batch_id = user_json_data['batch_id']
        thumbnail = image_array[image_index]
        message = user_json_data['message']
        Class = []
        Class.append(int(standard))

        data = {
            "action": "null",
            "class": Class,
            "batch_id": batch_id,
            "deadline_time": deadline,
            "message": message,
            "payload": test_id,
            "thumbnail": thumbnail,
            "time": date,
            "time_remaining": "",
            "type": "deadline"
        }
        doc_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

        db = firestore.Client()
        doc_ref = db.collection(u'announcement').document(str(teacher_id)).collection(batch_id).document(doc_id)

        doc_ref.set(data)

        return HttpResponse('Updated')


class testList(APIView):
    def get(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')

        username = claims['email'].split('@')[0]
        #username = "pablo"

        db = firestore.Client()
        doc_ref = db.collection(u'test').where(u'send_by', u'==', username)

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
                "sections": section,
                "batch_id": all_data['batch_id'],
                "time": all_data['test_time']
            }
            testList.append(data)
            #testList.reverse()
            #return HttpResponse(data['package'])
            #testList.append(el.to_dict())

        return HttpResponse(json.dumps(testList), content_type='application/json')

class viewTestData(APIView):
    def post(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')

        username = claims['email'].split('@')[0]
        #username = "pablo"

        user_json_data=json.loads(request.body)
        test_id = user_json_data['test_id']

        db = firestore.Client()
        #doc_ref = db.collection(u'test').where(u'test_id', u'==', test_id)
        doc_ref = db.collection(u'test').document(test_id)
        doc = doc_ref.get()
        allCourseBlocks = doc.to_dict()

        return JsonResponse(allCourseBlocks)


class admin_login(APIView):
    def get(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')

        username = claims['email'].split('@')[0]
        #username = "career_mentorAdmin"

        teachers_list = teacher_account.objects.filter(Type = username).values_list('username', flat=True)

        credentials = []

        for teacher in teachers_list:
            teachers_list = teacher_credentials.objects.select_related('teacher').get(username = teacher)

            data = {
                "name": teachers_list.teacher.firstname +' '+teachers_list.teacher.lastname,
                "photo": teachers_list.teacher.photo,
                "gender": teachers_list.teacher.gender,
                "username": teachers_list.username,
                "password": teachers_list.password
            }
            credentials.append(data)
        return Response(credentials)

class change_login(APIView):
    def get(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')

        username = claims['email'].split('@')[0]
        #username = "career_mentorAdmin"
        admin_username = teacher_account.objects.get(username = username).Type
        credentials = []

        if(admin_username == 'Individual'):
            teachers_list = teacher_credentials.objects.select_related('teacher').get(username = username)
            data = {
                "name": teachers_list.teacher.firstname +' '+teachers_list.teacher.lastname,
                "photo": teachers_list.teacher.photo,
                "gender": teachers_list.teacher.gender,
                "username": teachers_list.username,
                "password": teachers_list.password
            }
            credentials.append(data)
            return Response(credentials)



        teachers_list = teacher_account.objects.filter(Type = admin_username).values_list('username', flat=True)


        for teacher in teachers_list:
            teachers_list = teacher_credentials.objects.select_related('teacher').get(username = teacher)

            data = {
                "name": teachers_list.teacher.firstname +' '+teachers_list.teacher.lastname,
                "photo": teachers_list.teacher.photo,
                "gender": teachers_list.teacher.gender,
                "username": teachers_list.username,
                "password": teachers_list.password
            }
            credentials.append(data)
        return Response(credentials)


class get_today_schedule(APIView):
    def get(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')

        username = claims['email'].split('@')[0]
        #username = "pablo"

        my_date = datetime.date.today()
        day = calendar.day_name[my_date.weekday()]

        time_threshold = datetime.datetime.now() - datetime.timedelta(hours=24)

        teacher = teacher_account.objects.get(username = username)
        teacher_id = teacher.teacher.teacher_id
        if(day == 'Monday'):
            classes_list = teacher_batch_data.objects.filter(teacher__teacher_id = teacher_id, monday = True, class_end_timing__gt = time_threshold).order_by('class_start_timing').values_list('standard', 'batch_id', 'class_start_timing', 'class_end_timing', flat=False)
        elif(day == 'Tuesday'):
            classes_list = teacher_batch_data.objects.filter(teacher__teacher_id = teacher_id, tuesday = True, class_end_timing__gt = time_threshold).order_by('class_start_timing').values_list('standard', 'batch_id', 'class_start_timing', 'class_end_timing', flat=False)
        elif(day == 'Wednesday'):
            classes_list = teacher_batch_data.objects.filter(teacher__teacher_id = teacher_id, wednesday = True, class_end_timing__gt = time_threshold).order_by('class_start_timing').values_list('standard', 'batch_id', 'class_start_timing', 'class_end_timing', flat=False)
        elif(day == 'Thursday'):
            classes_list = teacher_batch_data.objects.filter(teacher__teacher_id = teacher_id, thursday = True, class_end_timing__gt = time_threshold).order_by('class_start_timing').values_list('standard', 'batch_id', 'class_start_timing', 'class_end_timing', flat=False)
        elif(day == 'Friday'):
            classes_list = teacher_batch_data.objects.filter(teacher__teacher_id = teacher_id, friday = True, class_end_timing__gt = time_threshold).order_by('class_start_timing').values_list('standard', 'batch_id', 'class_start_timing', 'class_end_timing', flat=False)
        elif(day == 'Saturday'):
            classes_list = teacher_batch_data.objects.filter(teacher__teacher_id = teacher_id, saturday = True, class_end_timing__gt = time_threshold).order_by('class_start_timing').values_list('standard', 'batch_id', 'class_start_timing', 'class_end_timing', flat=False)
        elif(day == 'Sunday'):
            classes_list = teacher_batch_data.objects.filter(teacher__teacher_id = teacher_id, sunday = True, class_end_timing__gt = time_threshold).order_by('class_start_timing').values_list('standard', 'batch_id', 'class_start_timing', 'class_end_timing', flat=False)
        else:
            classes_list = []

        upcoming_classes=[]

        for Class in classes_list:
            data = {
                "standard": Class[0],
                "batch_id": Class[1],
                "class_start_timing": Class[2],
                "class_end_timing": Class[3]
            }
            upcoming_classes.append(data)

        return Response(upcoming_classes)

@csrf_exempt
def send_attendance_notificaton(request):
    id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
    claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
    if not claims:
        return HttpResponse('Unauthorized')

    username = claims['email'].split('@')[0]
    #username = "pablo"

    user_json_data=json.loads(request.body)
    student_attendance_data = user_json_data['class_attended']
    #teacher_name = user_json_data['teacher']

    username_list = list(map(lambda x: x['username'], student_attendance_data))

    fcmTokenData = fcm_token.objects.filter(student__username__in = username_list).values_list('student__username', 'fcmToken', flat=False)
    #return JsonResponse(list(fcmTokenData), safe=False)
    for fcmToken in fcmTokenData:
        #return HttpResponse(fcmToken[0])
        for student in student_attendance_data:
            if(fcmToken[0]==student['username']):
                try:
                	if(student['class_attended']):
                		notification = messaging.Notification(title="Attention!!!", body="You were marked present in class today")
                		msg = messaging.Message(token=fcmToken[1], notification = notification, data={'title': "title", 'body': "message"})
                		msg_ = messaging.send(msg)
                	else:
                		notification = messaging.Notification(title="Attention!!!", body="You were marked absent in class today")
                		msg = messaging.Message(token=fcmToken[1], notification = notification, data={'title': "title", 'body': "message"})
                		msg_ = messaging.send(msg)
                except:
                    pass

    return HttpResponse('Successfully Sent')


@csrf_exempt
def cancel_class(request):
	id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
	claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
	if not claims:
		return HttpResponse('Unauthorized')

	username = claims['email'].split('@')[0]
	#username = "pablo"

	user_json_data=json.loads(request.body)
	standard = user_json_data['standard']
	batch_id = user_json_data['batch_id']
	date = user_json_data['date']

	teacher = teacher_account.objects.get(username = username)
	teacher_id = teacher.teacher.teacher_id
	name = teacher.teacher.firstname + ' ' + teacher.teacher.lastname
	coaching_name = teacher.teacher.coaching_name

	student_list = teacher_student_interaction.objects.filter(teacher__teacher_id = teacher_id, batch_id = batch_id, student__standard = standard).values_list('student__username', flat=True)

	fcmTokenData = fcm_token.objects.filter(student__username__in = student_list).values_list('student__username', 'fcmToken', flat=False)
	#return HttpResponse(fcmTokenData)
	for fcmToken in fcmTokenData:
		try:
			notification = messaging.Notification(title=name+' - '+ coaching_name, body="Class has been cancelled today")
			msg = messaging.Message(token=fcmToken[1], notification = notification, data={'title': "title", 'body': "message"})
			msg_ = messaging.send(msg)
		except:
			pass
		
	doc_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

	standard_array=[]
	standard_array.append(int(standard))

	data = {
			"action": "null",
			"message": "class cancelled",
			"class": standard_array,
			"time": date,
			"payload": '',
			"type": "announcement"
        }

	db = firestore.Client()
	doc_ref = db.collection(u'announcement').document(str(teacher_id)).collection(batch_id).document(doc_id)

	doc_ref.set(data)

	return HttpResponse('Successfully Sent')


class signup_request(APIView):
    def post(self, request):

        user_json_data=json.loads(request.body)
        name = user_json_data['name']
        phone_number = user_json_data['phone_number']

        this_dict = {
            "creatd_at": datetime.datetime.today(),
            "name": name,
            "phone_number": phone_number
        }

        doc_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

        db = firestore.Client()
        doc_ref = db.collection(u'signup_request').document(doc_id)
        doc_ref.set(this_dict)

        return HttpResponse('Successfully Sent')

@csrf_exempt
def update_parents_details(request):
    id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
    claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
    if not claims:
       return HttpResponse('Unauthorized')

    user_json_data=json.loads(request.body)
       
    student_info = user_info.objects.get(username=user_json_data['username'])
   
    try:
        if user_json_data['contact_number'] is not None:
            contact_number = user_json_data['contact_number'];
    except Exception as e:
        pass;
   
    chapter_object_object=parents_details(student=student_info, name = '', relationship_to_student='other', contact_number=contact_number)
    chapter_object_object.save()
    return JsonResponse({'status': 'True', 'message': 'Successfully updated'})

@csrf_exempt
def update_parents_details_full(request):
    id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
    claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
    if not claims:
       return HttpResponse('Unauthorized')

    user_json_data=json.loads(request.body)

   
    student_info = user_info.objects.get(username=user_json_data['username'])

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
def get_parents_details(request):
    id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
    claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
    if not claims:
       return HttpResponse('Unauthorized')

    user_json_data=json.loads(request.body)


    if parents_details.objects.filter(student__username=user_json_data['username']).exists():
        chapter_object_object=parents_details.objects.filter(student__username=user_json_data['username']).last()
        if(chapter_object_object.relationship_to_student == '1'):
            relationship_to_student = 'Father'
        elif(chapter_object_object.relationship_to_student == '2'):
            relationship_to_student = 'Mother'
        elif(chapter_object_object.relationship_to_student == '3'):
            relationship_to_student = 'Brother'
        elif(chapter_object_object.relationship_to_student == '4'):
            relationship_to_student = 'Sister'
        else:
            relationship_to_student = 'Other'

        data = {
            "name": chapter_object_object.name,
            "contact_number": chapter_object_object.contact_number,
            "relationship_to_student": relationship_to_student
        }
        return JsonResponse(data)
    data = {
        "name": '',
        "contact_number": '',
        "relationship_to_student": 'other'
        }
    return HttpResponse('working')


class livecourses(APIView):
    def get(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
           return HttpResponse('Unauthorized')

        username = claims['email'].split('@')[0]
        #username = "pablo"

        teacher = teacher_account.objects.get(username = username)
        teacher_id = teacher.teacher.teacher_id

        live_course_list = live_courses.objects.filter(teacher__teacher_id = teacher_id)
        
        result = []
        

        for course in live_course_list:
            data = {
            "course_id": course.course_id,
            "course_name": course.course_name,
            "teacher_id": teacher_id,
            "teacher": teacher.teacher.firstname+ ' '+teacher.teacher.lastname
            }

            result.append(data)

        return Response(result)


class fetchCourseBlocks(APIView):
    def get(self, request, courseid):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
           return HttpResponse('Unauthorized')

        if(courseid[0:2] == 'MA'):
            subject = 'Mathematics'
        elif(courseid[0:2] == 'CH'):
            subject = 'Chemistry'
        elif(courseid[0:2] == 'PH'):
            subject = 'Physics'
        else:
            subject = 'Null'

        db = firestore.Client()
        
        doc_ref = db.collection(u'courseDatabase').document(subject).collection(courseid).document(courseid)
        doc = doc_ref.get()
        allCourseBlocks = doc.to_dict()
        
        return JsonResponse(allCourseBlocks)


@csrf_exempt
def select_test_questions(request):
    id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
    claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
    if not claims:
        return HttpResponse('Unauthorized')

    #username = claims['firebase']['identities']['phone'][0][3:13]
    
    #ssc
    #exams_object=exams.objects.filter(course__exam_id=standard)
    data=json.loads(request.body)
    

    #exam_package_object = exams_package.objects.get(section=package)
    
    #sections = test_sections.objects.filter(exams_package = exam_package_object).values_list('section','section_name', flat=False)

    #return HttpResponse(sections[0][0])
    #no_of_sections = len(sections)

    #section_index = random.randint(0,no_of_sections-1)

    #return HttpResponse(sections[section_index])

    test_data = []
    db = firestore.Client()

    quesList=[]
    
    doc_ref = db.collection(u'new_question_database').document(u'exams').collection(data['class']).document(data['goal']).collection(data['subject']).where(u'section', u'==', data['section']).where(u'index', u'>=', data['index'])
    doc = doc_ref.limit(data['number_of_questions_per_sections']).get()
    #return HttpResponse(doc)
    #my_dict = { el.id: el.to_dict() for el in doc }
    for el in doc:
      quesList.append(el.to_dict())

    test_data.append(
        {
          "data": quesList,
          "end_index": quesList[-1]['index']
        }
      )
      
    return HttpResponse(json.dumps(test_data), content_type='application/json')


@csrf_exempt
def store_test_data(request):
    #id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
    #claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
    #if not claims:
    #  return HttpResponse('Unauthorized')

    #username = claims['email'].split('@')[0]
    username = "pablo"
    teacher = teacher_account.objects.get(username = username)
    teacher_id = teacher.teacher.teacher_id

    data=json.loads(request.body)
    standard = data['standard']

    goal = exam_info.objects.get(exam_id=standard)
    #ssc
    #exams_object=exams.objects.filter(course__exam_id=standard)

    package = data['exams_package']
    exam_name = data['exam_name']
    duration = data['duration']
    sections = data['chapters']
    test_time = data['test_time']
    batch_id = data['batch_id']
    blocks = data['blocks']
    total_questions = data['total_questions']

    db = firestore.Client()

    
    test_id = str(uuid.uuid4())

    final_data = {
        "test_id": test_id,
        "send_by": username,
        "class": standard,
        "send_by_id": teacher_id,
        "test_time": test_time,
        "package": package,
        "exam_name": exam_name,
        "duration": duration,
        "sections": sections,
        "blocks": blocks,
        "performance": [],
        "participants": [],
        "batch_id": batch_id,
        "no_of_questions": total_questions
    }

    doc_ref = db.collection(u'test').document(test_id)
    doc_ref.set(final_data)

    return HttpResponse(json.dumps(final_data), content_type='application/json')