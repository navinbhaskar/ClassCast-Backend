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
import google.oauth2.id_token
import google.auth.transport.requests
from .models import device_id

HTTP_REQUEST = google.auth.transport.requests.Request()



class get_device_id(APIView):
    def get(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')
        username1 = claims['firebase']['identities']['phone']
        username = username1[0][3:13]
        deviceId = device_id.objects.get(student__username=username)
        return HttpResponse(deviceId.device_id)

class get_device_id_updated(APIView):
    def get(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')
        username1 = claims['firebase']['identities']['phone']
        username = username1[0][3:13]
        
        try:
            deviceId = device_id.objects.get(student__username=username)
            return HttpResponse(deviceId.device_id)
        except:
            return HttpResponse(None)


class save_device_id(APIView):
    def post(self, request):
        id_token = request.META['HTTP_AUTHORIZATION'].split(' ').pop()
        claims = google.oauth2.id_token.verify_firebase_token(id_token, HTTP_REQUEST)
        if not claims:
            return HttpResponse('Unauthorized')
        data = request.data
        username1 = claims['firebase']['identities']['phone']
        username = username1[0][3:13]
        if device_id.objects.filter(student__username=username).exists():            
            return Response('Already Exists', status= 404)
        else:
            y = device_id()
            y.student = user_info.objects.get(username=username)
            y.device_id = data['device_id']
            y.save()
            return Response('created', status= 201)
        