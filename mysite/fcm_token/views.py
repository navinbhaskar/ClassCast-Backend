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
import google.oauth2.id_token
import google.auth.transport.requests
from .models import fcm_token
from django.views.decorators.csrf import csrf_exempt

HTTP_REQUEST = google.auth.transport.requests.Request()



class get_fcm_token(APIView):
    def get(self, request, username):
        #id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        #claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        #if not claims:
        #    return HttpResponse('Unauthorized')
        fcm = fcm_token.objects.get(student__username=username)
        return HttpResponse(fcm.fcmToken)

@csrf_exempt
def get_multiple_fcm_token(request):
    user_json_data=json.loads(request.body)
    usernameList = user_json_data['username']
    fcmTokenList = fcm_token.objects.filter(student__username__in = usernameList).values_list('fcmToken', flat=True)
    return JsonResponse(list(fcmTokenList), safe=False)

@csrf_exempt
def get_multiple_fcm_token_with_username(request):
    user_json_data=json.loads(request.body)
    usernameList = user_json_data['username']
    fcmTokenList = fcm_token.objects.filter(student__username__in = usernameList).values_list('student__username', 'fcmToken', flat=False)
    return JsonResponse(list(fcmTokenList), safe=False)

class save_fcm_token(APIView):
    def post(self, request):
        data = request.data
        if fcm_token.objects.filter(student__username=data['username']).exists():
            #return HttpResponse("working")
            fcm_token.objects.filter(student__username=data['username']).update(fcmToken=data['fcmToken'])
            return Response('Updated', status= 201)
        else:
            y = fcm_token()
            y.student = user_info.objects.get(username=data['username'])
            y.fcmToken = data['fcmToken']
            y.save()
            return Response('created', status= 201)
