from django.shortcuts import render
from rest_framework.views import APIView
from django.http import HttpResponse
from django.http import JsonResponse
import json
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
import datetime
import sys
sys.path.append("..")
from mysite.users.models import user_info
from mysite.teachers.models import teacher_info
import google.oauth2.id_token
import google.auth.transport.requests
from . models import course_details, chapter_details, student_course_interactions, access_code_coursewise, course_package, package_details, test_series_details, test_details, student_test_interactions, test_series_videos, course_test_series_list, course_package_details, access_code_test_series_wise, access_code_premium
from mysite.course_data.models import student_block_interactions
from django.views.decorators.csrf import csrf_exempt
import random
import string
from firebase_admin import firestore
import uuid
from mysite.teachers_app.models import teacher_account

HTTP_REQUEST = google.auth.transport.requests.Request()

class add_course_enrollment(APIView):
    def post(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')

        #username = "1111111133"
        username = claims['firebase']['identities']['phone'][0][3:13]

        json_data=json.loads(request.body)
        course_id=json_data['course_id']
        teacher_id=json_data['teacher_id']
        enrollment_method=json_data['enrollment_method']
        payement_mode=json_data['payement_mode']
        payment_id=json_data['payment_id']
        
        student=user_info.objects.get(username=username)
        teacher=teacher_info.objects.get(teacher_id = teacher_id)

        if(course_details.objects.filter(teacher = teacher, course_id = course_id).exists()):
            course = course_details.objects.get(teacher = teacher, course_id = course_id)

            if(student_course_interactions.objects.filter(student= student, course = course).exists()):
                return Response('Already Exists', status= 409)

            course_object = student_course_interactions(student = student, course = course, enrollment_method=enrollment_method, payement_mode=payement_mode, payment_id=payment_id, enrollment_status='Success')
            course_object.save()
                            
            return Response('Updated', status= 201)

        else:
            return Response('Course not found', status= 409)

class add_course_enrollment_new(APIView):
    def post(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')

        #username = "1111111133"
        username = claims['firebase']['identities']['phone'][0][3:13]

        json_data=json.loads(request.body)
        course_id=json_data['course_id']
        teacher_id=json_data['teacher_id']
        enrollment_method=json_data['enrollment_method']
        payement_mode=json_data['payement_mode']
        payment_id=json_data['payment_id']
        package_index=json_data['package_index']

        if(package_index == 0):
            selected_package = 'course'
        elif(package_index == 1):
            selected_package = 'course_plus_books'
        elif(package_index == 2):
            selected_package = 'only_books'
        else:
            selected_package = 'course'

        student=user_info.objects.get(username=username)
        teacher=teacher_info.objects.get(teacher_id = teacher_id)

        if(course_details.objects.filter(teacher = teacher, course_id = course_id).exists()):
            course = course_details.objects.get(teacher = teacher, course_id = course_id)

            if(student_course_interactions.objects.filter(student= student, course = course).exists()):
                return Response('Already Exists', status= 409)

            course_object = student_course_interactions(student = student, course = course, enrollment_method=enrollment_method, payement_mode=payement_mode, payment_id=payment_id, enrollment_status='Success', course_package = selected_package)
            course_object.save()
                            
            return Response('Updated', status= 201)

        else:
            return Response('Course not found', status= 409)

class get_course_list(APIView):
    def get(self, request, teacher_id):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')
        #username = "1111111133"
        username = claims['firebase']['identities']['phone'][0][3:13]

        result = []
        student = user_info.objects.get(username = username)
        course_list = course_details.objects.filter(teacher__teacher_id = teacher_id)
        

        for course in course_list:
            if(student_course_interactions.objects.filter(course=course, student = student).exists()):
                data = {
                "course_id": course.course_id,
                "course_name": course.course_name,
                "amount": course.amount,
                "course_details": course.course_details,
                "thumbnail": course.thumbnail,
                "books_available": course.books_available,
                "access_token_only": course.access_token_only,
                "enrolled": True
                }
            else:
                data = {
                "course_id": course.course_id,
                "course_name": course.course_name,
                "amount": course.amount,
                "course_details": course.course_details,
                "amount_course_plus_books": course.amount_course_plus_books,
                "amount_only_books": course.amount_only_books,
                "thumbnail": course.thumbnail,
                "books_available": course.books_available,
                "access_token_only": course.access_token_only,
                "enrolled": False
                }
            result.append(data)

        return Response(result)
        

class get_my_course_list(APIView):
    def get(self, request, teacher_id):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')
        #username = "1111111133"
        username = claims['firebase']['identities']['phone'][0][3:13]

        result = []
        student = user_info.objects.get(username = username)

        course_list = course_details.objects.filter(teacher__teacher_id = teacher_id)
        

        for course in course_list:
            if(student_course_interactions.objects.filter(course=course, student = student).exists()):
                data = {
                "course_id": course.course_id,
                "course_name": course.course_name,
                "amount": course.amount,
                "course_details": course.course_details,
                "thumbnail": course.thumbnail,
                "books_available": course.books_available,
                "enrolled": True
                }
                result.append(data)

        return Response(result)


class get_course_list_shyam(APIView):
    def get(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')
        #username = "1111111133"
        username = claims['firebase']['identities']['phone'][0][3:13]

        result = []
        student = user_info.objects.get(username = username)
        course_list = course_details.objects.filter(teacher__teacher_id = 10)
        

        for course in course_list:
            if(student_course_interactions.objects.filter(course=course, student = student).exists()):
                data = {
                "course_id": course.course_id,
                "course_name": course.course_name,
                "amount": course.amount,
                "course_details": course.course_details,
                "thumbnail": course.thumbnail,
                "enrolled": True
                }
            else:
                data = {
                "course_id": course.course_id,
                "course_name": course.course_name,
                "amount": course.amount,
                "course_details": course.course_details,
                "thumbnail": course.thumbnail,
                "enrolled": False
                }
            result.append(data)

        return Response(result)


class get_cahpter_list_shyam(APIView):
    def get(self, request, course_id):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')

        

        result = []
        course = course_details.objects.get(course_id = course_id)
        chapter_list = chapter_details.objects.filter(course=course)
        

        for chapter in chapter_list:

            data = {
            "course_id": chapter.chapter_id,
            "chapter_name": chapter.chapter_name,
            "details": chapter.chapter_details,
            "thumbnail": chapter.thumbnail
            }
            result.append(data)

        return Response(result)

class enrollment_from_token(APIView):
    def post(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')

        #username = "1111111133"
        username = claims['firebase']['identities']['phone'][0][3:13]

        json_data=json.loads(request.body)
        access_code=json_data['access_code']
        course_id=json_data['course_id']
        teacher_id=json_data['teacher_id']

        student=user_info.objects.get(username=username)

        if(course_details.objects.filter(teacher__teacher_id = teacher_id, course_id = course_id).exists()):
            course = course_details.objects.get(teacher__teacher_id = teacher_id, course_id = course_id)
        else: 
            return Response('Course not found', status= 409)

        try:
            access_code_object=access_code_coursewise.objects.get(access_code=access_code, course = course, expired=False)
            access_code_object.student = student
            access_code_object.expired = True
            access_code_object.save()

            if(student_course_interactions.objects.filter(student= student, course = course).exists()):
                return Response('Already Exists', status= 409)

            course_object = student_course_interactions(student = student, course = course, payement_mode='None', payment_id=access_code, enrollment_status='Success', enrollment_method='Token')
            course_object.save()
                                
            return Response('Updated', status= 201)

        except Exception as e:
            return HttpResponse(e)
            return Response('Invalid or Already Used', status=404)

        return Response('Invalid or Already Used', status=404)


class enrollment_from_token_new(APIView):
    def post(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')

        #username = "1111111133"
        username = claims['firebase']['identities']['phone'][0][3:13]

        json_data=json.loads(request.body)
        access_code=json_data['access_code']
        course_id=json_data['course_id']
        teacher_id=json_data['teacher_id']
        package_index=json_data['package_index']

        if(package_index == 0):
            selected_package = 'course'
        elif(package_index == 1):
            selected_package = 'course_plus_books'
        elif(package_index == 2):
            selected_package = 'only_books'
        else:
            selected_package = 'course'

        student=user_info.objects.get(username=username)

        if(course_details.objects.filter(teacher__teacher_id = teacher_id, course_id = course_id).exists()):
            course = course_details.objects.get(teacher__teacher_id = teacher_id, course_id = course_id)
        else: 
            return Response('Course not found', status= 409)

        try:
            access_code_object=access_code_coursewise.objects.get(access_code=access_code, course = course, expired=False)
            access_code_object.student = student
            access_code_object.expired = True
            access_code_object.save()

            if(student_course_interactions.objects.filter(student= student, course = course).exists()):
                return Response('Already Exists', status= 409)

            course_object = student_course_interactions(student = student, course = course, payement_mode='None', payment_id=access_code, enrollment_status='Success', enrollment_method='Token', course_package = selected_package)
            course_object.save()
                                
            return Response('Updated', status= 201)

        except Exception as e:
            return HttpResponse(e)
            return Response('Invalid or Already Used', status=404)

        return Response('Invalid or Already Used', status=404)

class generateAccessCode(APIView):
    def get(self, request, course_id, teacher_id, batch_id, number):
        #id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        #claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        #if not claims:
        #    return HttpResponse('Unauthorized')
        token_list=[]
        batch_list=[]
        course_list=[]

        course = course_details.objects.get(teacher__teacher_id = teacher_id, course_id = course_id)
        
        for i in range(int(number)):
            token = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            token_object=access_code_coursewise(course=course, access_code = token, batch_id=batch_id, expired=False)
            token_object.save()
            token_list.append(token)
            batch_list.append(batch_id)
            course_list.append(course_id)

        new_list = zip(course_list, batch_list, token_list)
        zipped = list(new_list)

        your_list_as_json = json.dumps(zipped)

        return HttpResponse(your_list_as_json, status=201 )


class get_test_series_list(APIView):
    def get(self, request, teacher_id):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')
        #username = "1111111133"
        username = claims['firebase']['identities']['phone'][0][3:13]

        result = []
        student = user_info.objects.get(username = username)
        test_series_list = test_series_details.objects.filter(teacher__teacher_id = teacher_id)
        

        for test_series in test_series_list:
            if(student_test_interactions.objects.filter(test_series=test_series, student = student).exists()):
                data = {
                "course_id": test_series.test_series_id,
                "course_name": test_series.test_series_name,
                "amount": test_series.amount,
                "course_details": test_series.test_series_details,
                "thumbnail": test_series.thumbnail,
                "thumbnail_free_test": test_series.thumbnail_free_test,
                "access_token_only": test_series.access_token_only,
                "enrolled": True,
                "free_test_available": test_series.free_test_available,
                "paid_test_available": test_series.paid_test_available
                }
            else:
                data = {
                "course_id": test_series.test_series_id,
                "course_name": test_series.test_series_name,
                "amount": test_series.amount,
                "course_details": test_series.test_series_details,
                "thumbnail": test_series.thumbnail,
                "thumbnail_free_test": test_series.thumbnail_free_test,
                "access_token_only": test_series.access_token_only,
                "enrolled": False,
                "free_test_available": test_series.free_test_available,
                "paid_test_available": test_series.paid_test_available
                }
            result.append(data)

        return Response(result)


class get_test_list(APIView):
    def get(self, request, test_series_id):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')

        #username = "1111111133"
        username = claims['firebase']['identities']['phone'][0][3:13]

        result = []
        test_series = test_series_details.objects.get(test_series_id = test_series_id)
        test_list = test_details.objects.filter(test_series=test_series)
        
        db = firestore.Client()

        for test in test_list:

            doc_ref = db.collection(u'Test_series_performance').where(u'test_id', u'==', test.test_id).where(u'student', u'==', username)
            doc = doc_ref.get()
            testList=[]
            for el in doc:
                testList.append(el.to_dict())

            data = {
            "test_id": test.test_id,
            "test_name": test.test_name,
            "thumbnail": test.thumbnail,
            "free": test.free,
            "test_details": test.test_details,
            "no_of_questions": test.no_of_questions,
            "pos_marks": test.pos_marks,
            "neg_marks": test.neg_marks,
            "assignment": test.assignment,
            "negative_marking": test.negative_marking,
            "duration": test.duration,
            "attempted": len(testList),
            "start_date": test.start_date,
            "end_date": test.end_date
            }
            result.append(data)

        return Response(result)


@csrf_exempt
def get_test_data(request, test_id):
    id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
    claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
    if not claims:
      return HttpResponse('Unauthorized')

    quesList = []
    db = firestore.Client()

    doc_ref = db.collection(u'Test_series').where(u'test_id', u'==', test_id)
    doc = doc_ref.get()

    for el in doc:
        #quesList.append(el.to_dict())
        return HttpResponse(json.dumps(el.to_dict()), content_type='application/json')

    return HttpResponse(json.dumps({'message': 'Test not found', 'status': 409}), content_type='application/json')


class add_test_enrollment(APIView):
    def post(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')

        #username = "1111111133"
        username = claims['firebase']['identities']['phone'][0][3:13]

        json_data=json.loads(request.body)
        test_series_id=json_data['test_series_id']
        teacher_id=json_data['teacher_id']
        enrollment_method=json_data['enrollment_method']
        payement_mode=json_data['payement_mode']
        payment_id=json_data['payment_id']
        #package_index=json_data['package_index']

        
        student=user_info.objects.get(username=username)
        teacher=teacher_info.objects.get(teacher_id = teacher_id)

        if(test_series_details.objects.filter(teacher = teacher, test_series_id = test_series_id).exists()):
            test_series = test_series_details.objects.get(teacher = teacher, test_series_id = test_series_id)

            if(student_test_interactions.objects.filter(student= student, test_series = test_series).exists()):
                return Response('Already Exists', status= 409)

            course_object = student_test_interactions(student = student, test_series = test_series, enrollment_method=enrollment_method, payement_mode=payement_mode, payment_id=payment_id, enrollment_status='Success')
            course_object.save()
                            
            return Response('Updated', status= 201)

        else:
            return Response('Test Series not found', status= 409)

@csrf_exempt
def store_test_performance(request):
    id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
    claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
    if not claims:
      return HttpResponse('Unauthorized')

    username = claims['firebase']['identities']['phone'][0][3:13]
    
    #username = "1111111133"

    data=json.loads(request.body)
    data['student'] = username
    data['timestamp'] = str(datetime.datetime.today())
    db = firestore.Client()

    doc_ref = db.collection(u'Test_series_performance').document(str(uuid.uuid4()))
    doc_ref.set(data)

    return HttpResponse('Updated')

@csrf_exempt
def get_previous_records(request, test_id):
    id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
    claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
    if not claims:
        return HttpResponse('Unauthorized')

    testList = []
    db = firestore.Client()

    #username = "1111111133"
    username = claims['firebase']['identities']['phone'][0][3:13]

    doc_ref = db.collection(u'Test_series_performance').where(u'student', u'==', username).where(u'test_id', u'==', test_id)
    doc = doc_ref.get()

    latest = {}

    previous_timestamp = '2018-02-11 18:44:49.729504'

    for el in doc:
        temp = el.to_dict()

        if(el.to_dict()['timestamp'] > previous_timestamp ):
            latest = temp
            previous_timestamp = el.to_dict()['timestamp']

        #test_name = test_details.objects.get(test_id=el.to_dict()['test_id'])
        #temp['test_name'] = test_name.test_name
        #testList.append(json.dumps(temp))
        #return HttpResponse(test_name.test_name)

    return HttpResponse(json.dumps(latest), content_type='application/json')


@csrf_exempt
def get_previous_records_all(request, teacher_id):
    id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
    claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
    if not claims:
        return HttpResponse('Unauthorized')

    testList = []
    db = firestore.Client()

    #username = "1111111133"
    username = claims['firebase']['identities']['phone'][0][3:13]

    teacherObject = teacher_info.objects.get(teacher_id = teacher_id)
    test_list = test_details.objects.filter(test_series__teacher = teacherObject).values_list('test_id', flat=True)

    doc_ref = db.collection(u'Test_series_performance').where(u'student', u'==', username)

    for test in test_list:
            try:
                doc = doc_ref.where(u'test_id', u'==', test).get()

                for el in doc:
                    temp = el.to_dict()
                    try:
                        test_name = test_details.objects.get(test_id=el.to_dict()['test_id'])
                        temp['test_name'] = test_name.test_name
                    except:
                        temp['test_name'] = ''
                    testList.append(temp)
            except:
                pass
        #return HttpResponse(test_name.test_name)

    return HttpResponse(json.dumps(testList), content_type='application/json')

class get_test_series_courses(APIView):
    def get(self, request, test_series_id):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')

        test_series_object = test_series_videos.objects.filter(test_series__test_series_id=test_series_id).first()
        
        db = firestore.Client()
        
        try:
            doc_ref = db.collection(u'Test_series_courses').document(test_series_object.course_id)
            doc = doc_ref.get()
            allCourseBlocks = doc.to_dict()
        except:
            allCourseBlocks = {}

        return JsonResponse(allCourseBlocks)


@csrf_exempt
def add_test(request):
        json_data=json.loads(request.body)
        test_id=json_data['test_id']
        test_name=json_data['test_name']
        test_detail=json_data['test_details']
        test_series_id=json_data['test_series_id']
        thumbnail=json_data['thumbnail']
        free=json_data['free']
        teacher_id=json_data['teacher_id']
        no_of_questions=json_data['no_of_questions']
        pos_marks=json_data['pos_marks']
        neg_marks=json_data['neg_marks']
        negative_marking=json_data['negative_marking']
        duration=json_data['duration']

        test_series = test_series_details.objects.get(teacher__teacher_id = teacher_id, test_series_id = test_series_id)

        test_object = test_details( test_id=test_id, test_name=test_name, test_details=test_detail, test_series=test_series, thumbnail=thumbnail, free=free, no_of_questions=no_of_questions, pos_marks=pos_marks, neg_marks=neg_marks, negative_marking=negative_marking, duration=duration )
        test_object.save()

        return HttpResponse('Success')



class get_course_test_series_list(APIView):
    def get(self, request, course_id):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')

        result = []

        test_series_list = course_test_series_list.objects.select_related('test_series').filter(course__course_id = course_id)
        

        for test_series_object in test_series_list:
            data = {
                "course_id": test_series_object.test_series.test_series_id,
                "course_name": test_series_object.test_series.test_series_name,
                "amount": test_series_object.test_series.amount,
                "course_details": test_series_object.test_series.test_series_details,
                "thumbnail": test_series_object.test_series.thumbnail,
                "thumbnail_free_test": test_series_object.test_series.thumbnail_free_test,
                "access_token_only": test_series_object.test_series.access_token_only
            }

            result.append(data)

        return Response(result)

class get_packages(APIView):
    def get(self, request, course_id):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')

        result = []

        test_series_list = course_package_details.objects.filter(course__course_id = course_id)
        

        for test_series_object in test_series_list:
            data = {
                "package_id": test_series_object.package_id,
                "package_name": test_series_object.package_name,
                "package_details": test_series_object.package_details,
                "amount": test_series_object.amount
            }

            result.append(data)

        return Response(result)


class add_course_enrollment_with_package(APIView):
    def post(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')

        #username = "1111111133"
        username = claims['firebase']['identities']['phone'][0][3:13]

        json_data=json.loads(request.body)
        course_id=json_data['course_id']
        teacher_id=json_data['teacher_id']
        enrollment_method=json_data['enrollment_method']
        payement_mode=json_data['payement_mode']
        payment_id=json_data['payment_id']
        package_index=json_data['package_index']
        package_id=json_data['package_id']

        if(package_index == 0):
            selected_package = 'course'
        elif(package_index == 1):
            selected_package = 'course_plus_books'
        elif(package_index == 2):
            selected_package = 'only_books'
        else:
            selected_package = 'course'

        student=user_info.objects.get(username=username)
        teacher=teacher_info.objects.get(teacher_id = teacher_id)

        if(course_details.objects.filter(teacher = teacher, course_id = course_id).exists()):
            course = course_details.objects.get(teacher = teacher, course_id = course_id)

            if(student_course_interactions.objects.filter(student= student, course = course).exists()):
                return Response('Already Exists', status= 409)

            course_object = student_course_interactions(student = student, course = course, enrollment_method=enrollment_method, payement_mode=payement_mode, payment_id=payment_id, enrollment_status='Success', course_package = selected_package, package = package_id)
            course_object.save()
                            
            return Response('Updated', status= 201)

        else:
            return Response('Course not found', status= 409)


class enrollment_from_token_test_series(APIView):
    def post(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')

        #username = "1111111133"
        username = claims['firebase']['identities']['phone'][0][3:13]

        json_data=json.loads(request.body)
        access_code=json_data['access_code']
        test_series_id=json_data['test_series_id']
        teacher_id=json_data['teacher_id']

        student=user_info.objects.get(username=username)

        if(test_series_details.objects.filter(teacher__teacher_id = teacher_id, test_series_id = test_series_id).exists()):
            test_series = test_series_details.objects.get(teacher__teacher_id = teacher_id, test_series_id = test_series_id)
        else: 
            return Response('Test Series not found', status= 409)

        try:

            if(student_test_interactions.objects.filter(student= student, test_series = test_series).exists()):
                return Response('Already Exists', status= 409)

            access_code_object=access_code_test_series_wise.objects.get(access_code=access_code, test_series = test_series, expired=False)
            access_code_object.student = student
            access_code_object.expired = True
            access_code_object.save()

            course_object = student_test_interactions(student = student, test_series = test_series, payement_mode='None', payment_id=access_code, enrollment_status='Success', enrollment_method='Token')
            course_object.save()
                                
            return Response('Updated', status= 201)

        except Exception as e:
            return HttpResponse(e)
            return Response('Invalid or Already Used', status=404)

        return Response('Invalid or Already Used', status=404)


@csrf_exempt
def add_chapter(request):
    json_data=json.loads(request.body)
    chapter_id=json_data['chapter_id']
    chapter_name=json_data['chapter_name']
    chapter_detail=json_data['chapter_details']
    course_id=json_data['course_id']
    thumbnail=json_data['thumbnail']
    teacher_id=json_data['teacher_id']

    course_object = course_details.objects.get(teacher__teacher_id = teacher_id, course_id = course_id)

    chapter_object = chapter_details( chapter_id=chapter_id, chapter_name=chapter_name, chapter_details=chapter_detail, course=course_object, thumbnail=thumbnail )
    chapter_object.save()

    return HttpResponse('Success')

@csrf_exempt
def get_overall_permormance(request, teacher_id):
    id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
    claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
    if not claims:
      return HttpResponse('Unauthorized')

    #username = "1111111133"
    username = claims['firebase']['identities']['phone'][0][3:13]

    db = firestore.Client()

    doc_ref = db.collection(u'Test_series_performance').where(u'student', u'==', username)
    doc = doc_ref.get()
    
    count = 0
    for el in doc:
        count += 1

    teacherObject = teacher_info.objects.get(teacher_id = teacher_id)
    course_list = course_details.objects.filter(teacher = teacherObject).values_list('course_id', flat=True)
    #chapter_list = chapter_details.objects.filter(course__teacher = teacherObject).values_list('chapter_id', flat=True)
    #return HttpResponse(course_list)

    video_watched = student_block_interactions.objects.filter(student__username=username, course_id__in = course_list).count()


    data = {
	    		'Number_of_Attempts': count, 
	    		'Video_Watched': video_watched
    }

    return HttpResponse(json.dumps(data), content_type='application/json')



class get_student_list_ta(APIView):
    def get(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')
        #username = 'the_optimist'
        username = claims['email'].split('@')[0]
        teacher = teacher_account.objects.get(username = username)
        teacher_id = teacher.teacher.teacher_id

        teacherObject = teacher_info.objects.get(teacher_id = teacher_id)
        course_list = student_course_interactions.objects.select_related('student', 'course').filter(course__teacher = teacherObject)
        
        result=[]

        for value in course_list:
            data = {
                "username": value.student.username,
                "name": value.student.firstname + " "+ value.student.lastname,
                "gender": value.student.gender,
                "courses": value.course.course_name
            }

            result.append(data)

        return Response(result)

class get_student_performance_ta(APIView):
    def get(self, request, student_username):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')
        #username = 'the_optimist'
        username = claims['email'].split('@')[0]
        teacher = teacher_account.objects.get(username = username)
        teacher_id = teacher.teacher.teacher_id

        teacherObject = teacher_info.objects.get(teacher_id = teacher_id)
        
        #course_list = course_details.objects.filter(teacher = teacherObject).values_list('course_id', flat=True)
        test_list = test_details.objects.filter(test_series__teacher = teacherObject).values_list('test_id', flat=True)
        #return HttpResponse(test_list)

        testList = []
        db = firestore.Client()

        doc_ref = db.collection(u'Test_series_performance').where(u'student', u'==', student_username)
        for test in test_list:
            try:
                doc = doc_ref.where(u'test_id', u'==', test).get()

                for el in doc:
                    temp = el.to_dict()
                    temp['sections']=[]
                    testList.append(temp)
            except:
                pass

        return HttpResponse(json.dumps(testList), content_type='application/json')


class get_test_list_ta(APIView):
    def get(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')
        #username = 'the_optimist'
        username = claims['email'].split('@')[0]
        teacher = teacher_account.objects.get(username = username)
        teacher_id = teacher.teacher.teacher_id

        teacherObject = teacher_info.objects.get(teacher_id = teacher_id)

        test_list = test_details.objects.filter(test_series__teacher = teacherObject).values_list('test_id', 'test_name', flat=False)

        test_array=[]

        for test in test_list:
            data = {
                "test_id": test[0],
                "test_name": test[1]
            }
            test_array.append(data)

        return Response(test_array)




class get_test_info_ta(APIView):
    def get(self, request, test_id):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')
        #username = 'the_optimist'
        username = claims['email'].split('@')[0]
        teacher = teacher_account.objects.get(username = username)
        teacher_id = teacher.teacher.teacher_id

        teacherObject = teacher_info.objects.get(teacher_id = teacher_id)
        
        #course_list = course_details.objects.filter(teacher = teacherObject).values_list('course_id', flat=True)
        test_list = test_details.objects.filter(test_series__teacher = teacherObject).values_list('test_id', flat=True)
        #return HttpResponse(test_list)

        testList = []
        db = firestore.Client()

        doc_ref = db.collection(u'Test_series').document(test_id)
        doc = doc_ref.get()
        allCourseBlocks = doc.to_dict()

        return HttpResponse(json.dumps(allCourseBlocks), content_type='application/json')

@csrf_exempt
def select_test_questions(request):
    id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
    claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
    if not claims:
        return HttpResponse('Unauthorized')

    data=json.loads(request.body)
    
    test_data = []
    db = firestore.Client()

    quesList=[]
    
    doc_ref = db.collection(u'optimist_question_database').where(u'index', u'>=', data['index'])
    doc = doc_ref.limit(data['number_of_questions_per_sections']).get()
    
    for el in doc:
      quesList.append(el.to_dict())

    test_data.append(
        {
          "data": quesList,
          "end_index": quesList[-1]['index']
        }
      )
      
    return HttpResponse(json.dumps(test_data), content_type='application/json')


class teacher_data_ts(APIView):
    def get(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')
        #username = 'the_optimist'
        username = claims['email'].split('@')[0]

        teacher = teacher_account.objects.get(username = username)
        teacher_id = teacher.teacher.teacher_id
        name = teacher.teacher.firstname + ' ' + teacher.teacher.lastname
        subject = teacher.teacher.subject
        teacher_photo = teacher.teacher.photo
        coaching_name = teacher.teacher.coaching_name
        area = teacher.teacher.area
        batches = teacher.teacher.batches
        classcast_select = teacher.teacher.classcast_select

        teacherObject = teacher_info.objects.get(teacher_id = teacher_id)
        
        course_list = course_details.objects.filter(teacher = teacherObject).count()

        student_list = student_course_interactions.objects.filter(course__teacher = teacherObject).values_list('student__username', flat=True)
        #return HttpResponse(len(set(student_list)))
        #student_count = teacher_student_interaction.objects.filter(teacher__teacher_id = teacher_id).count()

        data = {
            "username": username,
            "teacher_id": teacher_id,
            "name": name,
            "subject": subject,
            "photo": teacher_photo,
            "coaching_name": coaching_name,
            "area": area,
            "courses": course_list,
            "classcast_select": classcast_select,
            "batches": batches,
            "student_count": len(set(student_list))
        }
            #return HttpResponse(courseid)
        return Response(data)


class get_all_course_list_ta(APIView):
    def get(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')
        #username = 'the_optimist'
        username = claims['email'].split('@')[0]
        teacher = teacher_account.objects.get(username = username)
        teacher_id = teacher.teacher.teacher_id

        teacherObject = teacher_info.objects.get(teacher_id = teacher_id)
        course_list = course_details.objects.filter(teacher = teacherObject)
        
        result=[]

        for value in course_list:
            student_count = student_course_interactions.objects.filter(course__course_id = value.course_id).count()
            data = {
                "course_id": value.course_id,
                "course_name": value.course_name,
                "thumbnail": value.thumbnail,
                "course_details": value.course_details,
                "student_count": student_count
            }

            result.append(data)

        return Response(result)


class get_chapters_ta(APIView):
    def get(self, request, course_id):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')
        #username = 'the_optimist'
        username = claims['email'].split('@')[0]
        teacher = teacher_account.objects.get(username = username)
        teacher_id = teacher.teacher.teacher_id

        teacherObject = teacher_info.objects.get(teacher_id = teacher_id)
        #course = course_details.objects.get(course_id = course_id)
        chapter_list = chapter_details.objects.filter(course_id=course_id)
        
        result=[]

        for value in chapter_list:
            data = {
                "chapter_id": value.chapter_id,
                "chapter_name": value.chapter_name,
                "chapter_details": value.chapter_details,
                "thumbnail": value.thumbnail
            }

            result.append(data)

        return Response(result)


class get_all_performance_ta(APIView):
    def get(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')
        #username = 'the_optimist'
        username = claims['email'].split('@')[0]
        teacher = teacher_account.objects.get(username = username)
        teacher_id = teacher.teacher.teacher_id

        teacherObject = teacher_info.objects.get(teacher_id = teacher_id)
        
        #course_list = course_details.objects.filter(teacher = teacherObject).values_list('course_id', flat=True)
        test_list = test_details.objects.filter(test_series__teacher = teacherObject).values_list('test_id', 'test_name', flat=False)
        #return HttpResponse(test_list)

        testList = []
        db = firestore.Client()

        doc_ref = db.collection(u'Test_series_performance')
        for test in test_list:
            try:
                doc = doc_ref.where(u'test_id', u'==', test[0]).get()

                for el in doc:
                    temp = el.to_dict()
                    student=user_info.objects.get(username=temp['student'])
                    temp['name'] = student.firstname + ' ' + student.lastname
                    temp['test_name'] = test[1]
                    if 'marks' not in temp:
                        temp['marks'] = 0
                    if 'attempted' not in temp:
                        temp['attempted'] = 0
                    if 'correct' not in temp:
                        temp['correct'] = 0
                    temp['sections']=[]
                    testList.append(temp)
            except:
                pass

        return HttpResponse(json.dumps(testList), content_type='application/json')


class get_student_list_coursewise_ta(APIView):
    def get(self, request, course_id):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')
        #username = 'the_optimist'
        username = claims['email'].split('@')[0]
        teacher = teacher_account.objects.get(username = username)
        teacher_id = teacher.teacher.teacher_id

        teacherObject = teacher_info.objects.get(teacher_id = teacher_id)
        course_list = student_course_interactions.objects.select_related('student').filter(course__teacher = teacherObject, course__course_id=course_id)
        
        result=[]

        for value in course_list:
            data = {
                "username": value.student.username,
                "name": value.student.firstname + " "+ value.student.lastname,
                "gender": value.student.gender
            }

            result.append(data)

        return Response(result)


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
            "standard": student.standard
        }

        return Response(data)


@csrf_exempt
def get_premium(request):
    id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
    claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
    if not claims:
      return HttpResponse('Unauthorized')

    #username = "1111111133"
    username = claims['firebase']['identities']['phone'][0][3:13]

    student=user_info.objects.get(username=username)

    json_data=json.loads(request.body)
    access_code=json_data['access_code']
    teacher_id=json_data['teacher_id']

    if(access_code_premium.objects.filter(access_code=access_code, teacher__teacher_id=teacher_id, expired=False).exists()):
        access_code_object=access_code_premium.objects.get(access_code=access_code, teacher__teacher_id=teacher_id, expired=False)
        access_code_object.student = student
        access_code_object.expired = True
        access_code_object.save()

        course_list = course_details.objects.filter(teacher__teacher_id = teacher_id)#.values_list('course_id', flat=True)
        
        test_series_list = test_series_details.objects.filter(teacher__teacher_id = teacher_id)#.values_list('test_series_id', flat=True)

        for course_id in course_list:
            if(student_course_interactions.objects.filter(student= student, course = course_id).exists()):
                pass
            else:
                course_object = student_course_interactions(student = student, course = course_id, payement_mode='None', payment_id=access_code, enrollment_status='Success', enrollment_method='Token')
                course_object.save()

        for test_series_id in test_series_list:
            if(student_test_interactions.objects.filter(student= student, test_series = test_series_id).exists()):
                pass
            else:
                test_series_object = student_test_interactions(student = student, test_series = test_series_id, payement_mode='None', payment_id=access_code, enrollment_status='Success', enrollment_method='Token')
                test_series_object.save()

        return JsonResponse({'response': 'Success', 'status': 201})

    else:
        return JsonResponse({'error': 'Invalid Access Code', 'status': 409})