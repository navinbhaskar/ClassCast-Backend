from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import teachers_serializer, teacher_student_interaction_serializer, teacher_student_interaction_serializer1
from .models import teacher_info, teacher_student_interaction, course_enrollment
from django.http import HttpResponse
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
import json
import datetime
import sys
sys.path.append("..")
from mysite.users.models import user_info
from mysite.course_data.models import student_block_interactions, crashcourse_enrollment, live_courses
import google.oauth2.id_token
import google.auth.transport.requests
from firebase_admin import firestore
from django.core import serializers

HTTP_REQUEST = google.auth.transport.requests.Request()


class AllTeachersList(APIView):
    def get(self, request, subject, goal):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')

        if (goal=="all" and subject=="all"):
            teacherList = teacher_info.objects.all()
            serializer = teachers_serializer(teacherList, many = True)
            return Response(serializer.data)

        if goal=="all":
            teacherList = teacher_info.objects.filter(subject = subject)
            serializer = teachers_serializer(teacherList, many = True)
            return Response(serializer.data)
        
        teacherList = teacher_info.objects.filter(subject = subject, goal = goal)
        serializer = teachers_serializer(teacherList, many = True)
        return Response(serializer.data)

class availableTeachers(APIView):
    def get(self, request, username):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')  
        availableTeacher=[] 
        myTeachersList = teacher_student_interaction.objects.filter(student__username = username).values_list('teacher', flat=True)

        allTeacherList = teacher_info.objects.values_list('teacher_id', flat=True)
        #allTeacherList = teacher_info.objects.select_related('teacher').values_list('teacher_id', flat=True)
        #available_teacher = list(set(allTeacherList).difference(set(myTeachersList)))

        #a = allTeacherList.filter(teacher_id__in = available_teacher)
        #serializer = teachers_serializer(a, many = True)
        #return HttpResponse(serializer.data)
        #return HttpResponse(list(set(allTeacherList).difference(set(myTeachersList))))
        for teacher in allTeacherList:
            if teacher not in myTeachersList:
                availableTeacherObject = teacher_info.objects.get(teacher_id = teacher)
                serializer = teachers_serializer(availableTeacherObject)
                teachers_data = {
                    "firstname" : serializer.data['firstname'],
                    "lastname" : serializer.data['lastname'],
                    "teacher_id" : serializer.data['teacher_id'],
                    "gender" : serializer.data['gender'],
                    "classes" : serializer.data['classes'],
                    "qualification" : serializer.data['qualification'],
                    "pincode" : serializer.data['pincode'],
                    "rating" : serializer.data['rating'],
                    "about" : serializer.data['about'],
                    "courses" : serializer.data['courses'],
                    "batches" : serializer.data['batches'],
                    "subject" : serializer.data['subject'],
                    "photo" : serializer.data['photo'],
                    "coaching_name" : serializer.data['coaching_name'],
                    "area" : serializer.data['area'],
                    "goal" : serializer.data['goal'],
                    "class" : serializer.data['classes'],
                    "classcast_select": serializer.data['classcast_select'],
                    "number_of_courses" : len(serializer.data['courses'].split(',')),
                    "about" : serializer.data['about']
                }
                availableTeacher.append(teachers_data)
                #return HttpResponse(serializer.data['firstname'])
        return Response(availableTeacher)


class MyTeachersList(APIView):
    def get(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')
        
        username1 = claims['firebase']['identities']['phone']
        username = username1[0][3:13]
        
        result = []
        teacherList = teacher_student_interaction.objects.select_related('teacher').filter(student__username = username)
        #res_json = serializers.serialize('json', teacherList)
        for book in teacherList:
            #return HttpResponse(book.batch_id)
            serializer = teachers_serializer(book.teacher).data
            serializer['batch_id'] = book.batch_id
            result.append(serializer)
        return Response(result)
        
        


class StudentRequest(APIView):
    def post(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')
        data=request.data
        teachers=teacher_student_interaction.objects.filter(student__username=data['student'])
        teachers1=list(teachers)

        student=user_info.objects.get(username=data['student'])
        
        for item in data['teachers']:
            
            teacher=teacher_info.objects.get(teacher_id = item)
            teacher_object=teacher_student_interaction(student=student, teacher=teacher, batch_id = "none", is_approved=False, is_active=True, date_joined=datetime.datetime.now())
            teacher_object.save()
            try:
                this_batch=teacher_student_interaction.objects.get(student=student, teacher=teacher)
                course = teacher.courses.split(',')
                for course_id in course:
                    if not course_id:
                        pass;
                    else:
                        course_object = course_enrollment(student = student, course_id = course_id, batch = this_batch, date_joined = datetime.datetime.now())
                        course_object.save()
            except:
                pass;

                        
        return Response('Updated', status= 201)



class teachercoursedata(APIView):
    def get(self, request, teacherid):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')
        #username = claims['firebase']['identities']['phone']
        username1 = claims['firebase']['identities']['phone']
        username = username1[0][3:13]
        student_info = user_info.objects.get(username=username)
        #return HttpResponse(student_info.standard)
        #student=user_info.objects.get(username=username)
        try:
            if(teacher_student_interaction.objects.filter(student__username=username ,teacher=teacherid).exists()):
                teacher_enrolled = True
            else:
                teacher_enrolled = False

        except:
            teacher_enrolled = False
            return HttpResponse("notworking")
        teacher = teacher_info.objects.get(teacher_id = teacherid)
        teacherName = teacher.firstname
        course = teacher.courses.split(',')
        courselist=[]


        db = firestore.Client()
        db1 = db.collection(u'courseDatabase').document(teacher.subject)
        for item in course:
            courseid = item.split('+')[1]

            if(courseid[2:4] != student_info.standard and student_info.standard != '13'):
                continue;
            
            try:
                doc_ref = db1.collection(courseid).document(courseid)
                doc = doc_ref.get()
                allCourseBlocks = doc.to_dict()

                number_of_videos = 0
                number_of_assignment=0
                number_of_pdf=0

                block_id = allCourseBlocks['root']
                course_id1 = 'course-v1:'+block_id.split(':')[1]
                temp = course_id1.split('+')[0:3]
                course_id = '+'.join(temp)
                display_image = allCourseBlocks['display_image']
                display_name = allCourseBlocks['display_name']
                info = allCourseBlocks['info']
                start_date = allCourseBlocks['released_date']
                number_of_videos = allCourseBlocks['video']
                number_of_pdf = allCourseBlocks['pdf']
                number_of_assignment = allCourseBlocks['assignment']

                #if course_enrollment.objects.filter(student__username=username, course_id=course_id).exists():
                #    enrolled = course_enrollment.objects.filter(student__username=username, course_id=course_id).values_list('is_enrolled', flat=True)
                #    is_enrolled = enrolled[0]
                #else:
                #    is_enrolled = False

                if student_block_interactions.objects.filter(student__username=username, course_id=courseid).exists():
                    user_blocks_count = student_block_interactions.objects.filter(student__username=username, course_id=courseid).count()
                    completion = (user_blocks_count/number_of_videos) * 100
                else:
                    completion = 0
            except Exception as e:
                pass

                
            try:
                course_data = {
                    "block_id" : courseid,
                    "number_of_videos" : number_of_videos,
                    "number_of_assignment": number_of_assignment,
                    "number_of_pdf" : number_of_pdf,
                    "display_image" : display_image,
                    "display_name" : display_name,
                    "course_info" : info,
                    "percentage_completion" : round(completion,2),
                    "start_date" : start_date
                }
                courselist.append(course_data)

            except:
                pass

        data = {
            "teacher_enrolled" : teacher_enrolled,
            "data" : courselist
        }
            #return HttpResponse(courseid)
        return Response(data)


class teachercoursedatanew(APIView):
    def get(self, request, teacherid):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')
        #username = claims['firebase']['identities']['phone']
        username1 = claims['firebase']['identities']['phone']
        username = username1[0][3:13]
        student_info = user_info.objects.get(username=username)
        #return HttpResponse(student_info.standard)
        #student=user_info.objects.get(username=username)
        try:
            if(teacher_student_interaction.objects.filter(student__username=username ,teacher=teacherid).exists()):
                teacher_enrolled = True
            else:
                teacher_enrolled = False

        except:
            teacher_enrolled = False
            return HttpResponse("notworking")
        teacher = teacher_info.objects.get(teacher_id = teacherid)
        teacherName = teacher.firstname
        course = teacher.courses.split(',')
        courselist=[]


        db = firestore.Client()
        db1 = db.collection(u'courseDatabase').document(teacher.subject)
        for item in course:
            courseid = item.split('+')[1]

            if(courseid[2:4] != student_info.standard and student_info.standard != '13'):
                continue;
            
            try:
                doc_ref = db1.collection(courseid).document(courseid)
                doc = doc_ref.get()
                allCourseBlocks = doc.to_dict()

                number_of_videos = 0
                number_of_assignment=0
                number_of_pdf=0

                block_id = allCourseBlocks['root']
                course_id1 = 'course-v1:'+block_id.split(':')[1]
                temp = course_id1.split('+')[0:3]
                course_id = '+'.join(temp)
                display_image = allCourseBlocks['display_image']
                display_name = allCourseBlocks['display_name']
                info = allCourseBlocks['info']
                start_date = allCourseBlocks['released_date']
                number_of_videos = allCourseBlocks['video']
                number_of_pdf = allCourseBlocks['pdf']
                number_of_assignment = allCourseBlocks['assignment']

            except Exception as e:
                pass

                
            try:
                course_data = {
                    "block_id" : courseid,
                    "number_of_videos" : number_of_videos,
                    "number_of_assignment": number_of_assignment,
                    "number_of_pdf" : number_of_pdf,
                    "display_image" : display_image,
                    "display_name" : display_name,
                    "course_info" : info,
                    "start_date" : start_date
                }
                courselist.append(course_data)

            except:
                pass

        data = {
            "teacher_enrolled" : teacher_enrolled,
            "data" : courselist
        }
            #return HttpResponse(courseid)
        return Response(data)


class getpercentagecompletion(APIView):
    def get(self, request, courseid):

        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')
        
        username1 = claims['firebase']['identities']['phone']
        username = username1[0][3:13]
        

        if(courseid[0:2] == 'MA'):
            subject = 'Mathematics'
        elif(courseid[0:2] == 'CH'):
            subject = 'Chemistry'
        elif(courseid[0:2] == 'PH'):
            subject = 'Physics'
        else:
            subject = 'Null'

        db = firestore.Client()
        db1 = db.collection(u'courseDatabase').document(subject)

        try:
            doc_ref = db1.collection(courseid).document(courseid)
            doc = doc_ref.get()
            allCourseBlocks = doc.to_dict()

            number_of_videos = 0
            number_of_assignment=0
            number_of_pdf=0

            number_of_videos = allCourseBlocks['video']
            number_of_pdf = allCourseBlocks['pdf']
            number_of_assignment = allCourseBlocks['assignment']

        except Exception as e:
            pass

        if student_block_interactions.objects.filter(student__username=username, course_id=courseid).exists():
            user_blocks_count = student_block_interactions.objects.filter(student__username=username, course_id=courseid).count()
            
            if(number_of_videos+number_of_assignment+number_of_pdf != 0):
                completion = (user_blocks_count/(number_of_videos+number_of_assignment+number_of_pdf)) * 10
            else:
                completion = 0
        else:
            completion = 0

        return HttpResponse(completion)


class getCompletionBlocks(APIView):
    def get(self, request, courseid):

        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')
        
        username = claims['firebase']['identities']['phone'][0][3:13]
        #username="1111111133"

        blocks = student_block_interactions.objects.filter(student__username=username, course_id=courseid).values_list('block', flat=True)

        return Response(blocks)

class getRecentCompletedBlocks(APIView):
    def get(self, request):

        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')
        
        username = claims['firebase']['identities']['phone'][0][3:13]
        #username="1111111133"
        student_info = user_info.objects.get(username=username)
        standard = student_info.standard

        db = firestore.Client()

        starting_chapters = []
        if(standard == "11"):
            starting_chapters=[{"chapter_name": 'Some Basic Concepts of Chemistry', "subject": "Chemistry"}, {"chapter_name": 'Units and Measurements', "subject": "Physics"}, {"chapter_name": 'Relations and Functions', "subject": "Mathematics"}, {"chapter_name": 'Structure of Atom', "subject": "Chemistry"}, {"chapter_name": 'Motion in A Straight Line', "subject": "Physics"}, {"chapter_name": 'Trigonometric Functions', "subject": "Mathematics"}]
        elif(standard == "12"):
            starting_chapters=[{"chapter_name": "The Solid State", "subject": "Chemistry"}, {"chapter_name": "Electric Charges And Fields", "subject": "Physics"}, {"chapter_name": "Relations and Functions", "subject": "Mathematics"}, {"chapter_name": "Solutions", "subject": "Chemistry"}, {"chapter_name": "Electrostatic Potential And Capacitance", "subject": "Physics"}, {"chapter_name": "Matrices", "subject": "Mathematics"}]
        elif(standard == "13"):
            starting_chapters=[{"chapter_name": "The Solid State", "subject": "Chemistry"}, {"chapter_name": "Electric Charges And Fields", "subject": "Physics"}, {"chapter_name": "Relations and Functions", "subject": "Mathematics"}, {"chapter_name": "Solutions", "subject": "Chemistry"}, {"chapter_name": "Electrostatic Potential And Capacitance", "subject": "Physics"}, {"chapter_name": "Matrices", "subject": "Mathematics"}]
        elif(standard == 'SSC'):
            starting_chapters=[{"chapter_name": "General Intelligence & Reasoning", "subject": "SSC CPO 2018 Paper 1 Pack"}, {"chapter_name": "English", "subject": "SSC CPO 2018 Paper 1 Pack"}, {"chapter_name": "General Knowledge & Awareness", "subject": "SSC CPO 2018 Paper 1 Pack"}, {"chapter_name": "Quantitative Aptitude", "subject": "SSC CPO 2018 Paper 1 Pack"}]
        elif(standard == "9"):
            starting_chapters=[{"chapter_name": "number-systems", "subject": "Mathematics"}, {"chapter_name": "polynomials", "subject": "Mathematics"}, {"chapter_name": "coordinate-geometry", "subject": "Mathematics"}, {"chapter_name": "sound", "subject": "Science"}, {"chapter_name": "structure-of-the-atom", "subject": "Science"}, {"chapter_name": "motion", "subject": "Science"}]
        elif(standard == "10"):
            starting_chapters=[{"chapter_name": "real-numbers", "subject": "Mathematics"}, {"chapter_name": "polynomials", "subject": "Mathematics"}, {"chapter_name": "quadratic-equations", "subject": "Mathematics"}, {"chapter_name": "refraction-of-light", "subject": "Science"}, {"chapter_name": "reflection-of-light", "subject": "Science"}, {"chapter_name": "acids-bases-and-salts", "subject": "Science"}]
        else:
            starting_chapters=[]


        blocks = student_block_interactions.objects.filter(student__username=username).values_list('course_id', flat=True)
        

        #new_blocks=[]
        b = list(blocks)
        b.reverse()
        output = []
        for x in b:
            if x not in output:
                output.append(x)

        test_list=[]

        count = 0
        for item in output:
            count += 1
            if(count == 6):
                break
            if(item[0:2] == 'MA'):
                subject = 'Mathematics'
            elif(item[0:2] == 'CH'):
                subject = 'Chemistry'
            elif(item[0:2] == 'PH'):
                subject = 'Physics'
            else:
                break

            doc_ref = db.collection(u'courseDatabase').document(subject).collection(item).document(item)
            doc = doc_ref.get()
            allCourseBlocks = doc.to_dict()
            data = {
                "subject": subject,
                "course_id": item,
                "chapter_name": allCourseBlocks['display_name']
            }
            test_list.append(data)
         
        remaining_no_test = 8 - len(test_list)

        if(remaining_no_test > 0 ):
            test_list = test_list + starting_chapters[0:remaining_no_test-1]
            #return HttpResponse(starting_chapters[0:remaining_no_test])

        return Response(test_list)


class recommendedTestData(APIView):
    def post(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')

        data=request.data
        subject = data['subject']
        chapter = data['chapter']


        db = firestore.Client()
        museums = db.collection_group(subject)\
            .where("section", "==", chapter)
        docs = museums.limit(20).stream()

        questions=[]

        for doc in docs:
            questions.append(doc.to_dict())


        test_data=[]

        test_data.append(
          {
            "section": data['chapter'],
            "section_name": data['chapter'],
            "data": questions
          }
        )
      
        return HttpResponse(json.dumps(test_data), content_type='application/json')


class idToTeacherName(APIView):
    def get(self, request, teacher_id):
        teacher = teacher_info.objects.get(teacher_id = teacher_id)

        if(teacher.gender == '1'):
            gender = "Sir"
        else:
            gender = "Ma'am"

        name = teacher.firstname + ' ' + teacher.lastname + ' ' + gender


        return HttpResponse(name)


class idToTeacherDetails(APIView):
    def get(self, request, teacher_id):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')
        
        availableTeacherObject = teacher_info.objects.get(teacher_id = teacher_id)
        serializer = teachers_serializer(availableTeacherObject)

        return Response(serializer.data)


class MyCrashCourseList(APIView):
    def get(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')

        #username = "1111111133"
        username = claims['firebase']['identities']['phone'][0][3:13]
        
        result = []
        course_list = crashcourse_enrollment.objects.select_related('course__teacher').filter(student__username = username)
        

        for course in course_list:
            data = {
            "course_id": course.course.course_id,
            "course_name": course.course.course_name,
            "teacher_id": course.course.teacher.teacher_id,
            "teacher": course.course.teacher.firstname+ ' '+course.course.teacher.lastname,
            "gender": course.course.teacher.gender,
            "subject": course.course.teacher.subject
            }
            result.append(data)

        return Response(result)


class enroll_student(APIView):
    def get(self, request, teacher_id, course_id):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')

        #username = "1111111133"
        username = claims['firebase']['identities']['phone'][0][3:13]

        student=user_info.objects.get(username=username)
        teacher = teacher=teacher_info.objects.get(teacher_id = teacher_id)

        if(live_courses.objects.filter(teacher = teacher, course_id = course_id).exists()):
            course = live_courses.objects.get(teacher = teacher, course_id = course_id)

            if(crashcourse_enrollment.objects.filter(student= student, course = course).exists()):
                return Response('Already Exists', status= 409)

            course_object = crashcourse_enrollment(student = student, course = course, is_approved = True, date_joined = datetime.datetime.now())
            course_object.save()
                            
            return Response('Updated', status= 201)

        else:
            return Response('Course not found', status= 409)

class add_crashcourse_enrollment(APIView):
    def post(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')

        #username = "1111111133"
        username = claims['firebase']['identities']['phone'][0][3:13]
        student=user_info.objects.get(username=username)

        data=request.data['data']
        
        for item in data:
            
            teacher = teacher=teacher_info.objects.get(teacher_id = item['teacher_id'])

            if(live_courses.objects.filter(teacher = teacher, course_id = item['course_id']).exists()):
                course = live_courses.objects.get(teacher = teacher, course_id = item['course_id'])

                if(crashcourse_enrollment.objects.filter(student= student, course = course).exists()):
                    pass

                course_object = crashcourse_enrollment(student = student, course = course, is_approved = True, date_joined = datetime.datetime.now())
                course_object.save()
                                
        return Response('Updated', status= 201)
