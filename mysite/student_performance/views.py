from django.shortcuts import render
from rest_framework.views import APIView
from django.http import HttpResponse
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from datetime import date, timedelta
import sys
import json
sys.path.append("..")
from mysite.users.models import user_info
from mysite.course_data.models import student_block_interactions
import random
import string
from firebase_admin import firestore
import google.oauth2.id_token
import google.auth.transport.requests

HTTP_REQUEST = google.auth.transport.requests.Request()


class storePerformancePoints(APIView):
    def post(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')
        username1 = claims['firebase']['identities']['phone']
        username = username1[0][3:13]
        data=request.data

        today_date=date.today()
        points=data['points']

        db = firestore.Client()
        #
        doc_ref = db.collection(u'performance').document(username)
        doc = doc_ref.get()
        allCourseBlocks = doc.to_dict()

        try:
            totalPoints = sum(allCourseBlocks.values())
        except:
            totalPoints = 0 

        student_info = user_info.objects.get(username=username)
        student_info.karma_point = int(points) + int(totalPoints);
        student_info.save()

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

        return Response(today_date)

class getPerformance(APIView):
    def get(self, request, username):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')
        day0=date.today()
        day1=date.today() - timedelta(days=1)
        day2=date.today() - timedelta(days=2)
        day3=date.today() - timedelta(days=3)
        day4=date.today() - timedelta(days=4)
        day5=date.today() - timedelta(days=5)
        day6=date.today() - timedelta(days=6)

        db = firestore.Client()
        
        doc_ref = db.collection(u'performance').document(username)
        doc = doc_ref.get()
        allCourseBlocks = doc.to_dict() 

        try:
            day0_score = allCourseBlocks[str(day0)]
        except:
            day0_score = 0
        try:
            day1_score = allCourseBlocks[str(day1)]
        except:
            day1_score = 0
        try:
            day2_score = allCourseBlocks[str(day2)]
        except:
            day2_score = 0
        try:
            day3_score = allCourseBlocks[str(day3)]
        except:
            day3_score = 0
        try:
            day4_score = allCourseBlocks[str(day4)]
        except:
            day4_score = 0
        try:
            day5_score = allCourseBlocks[str(day5)]
        except:
            day5_score = 0
        try:
            day6_score = allCourseBlocks[str(day6)]
        except:
            day6_score = 0

        #Dict = {
        #    "day-0": day0_score,
        #    "day-1": day1_score,
        #    "day-2": day2_score,
        #    "day-3": day3_score,
        #    "day-4": day4_score,
        #    "day-5": day5_score,
        #    "day-6": day6_score
        #}


        return Response([day6_score,day5_score,day4_score,day3_score,day2_score,day1_score,day0_score])


class getKaramPoints(APIView):
    def get(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')
        username1 = claims['firebase']['identities']['phone']
        username = username1[0][3:13]
        #position = user_info.objects.all().order_by('karma_point').count()
        #marks = user_info.objects.all().values_list('karma_point', flat=True)
        #return HttpResponse(marks)
        marks=[]
        student= user_info.objects.all()
        for stud in student.iterator():
            if(stud.karma_point != ''):
                marks.append(int(stud.karma_point))

        marks.sort(reverse=True)
        #karma_point = user_info.objects.filter(username=username).values_list('karma_point', flat=True)
        student1 = user_info.objects.get(username = username)
        karma_point = student1.karma_point
        if(karma_point != ''):
            karma_point = int(karma_point)
        else:
            karma_point = 0

        rank = marks.index(karma_point)+1
        #return HttpResponse(marks.index(karma_point))
        #data_details = {'Rank' : marks.index(karma_point)+1, '-Score' : karma_point}
        #return HttpResponse(json.dumps(data_details))
        #return HttpResponse(student)
        user_blocks_count = 0
        if student_block_interactions.objects.filter(student__username=username).exists():
            user_blocks_count = student_block_interactions.objects.filter(student__username=username).count()

        db = firestore.Client()
        try:
            doc_ref = db.collection(u'performance').document(username)
            doc = doc_ref.get()
            allCourseBlocks = doc.to_dict()

            total_karma_points = sum(allCourseBlocks.values())
            #return HttpResponse(sum(allCourseBlocks.values()))
        except:
            total_karma_points = 0

        data_details = {'Rank' : rank*rank + 273, 'Score' : total_karma_points, 'Video_count': user_blocks_count}
        return HttpResponse(json.dumps(data_details))
            #return HttpResponse(0)
