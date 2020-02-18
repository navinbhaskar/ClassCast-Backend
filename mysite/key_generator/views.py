from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from mysite.license_provider.models import KeyModel
from mysite.license_provider.models import ContentModel
import jwt
import subprocess
import base64
import os, binascii
import hexdump

class KeyGenerator(APIView):
    def post(self, request, format=None):
        request_token = request.POST['request']
        
        # validate request is from verified server
        module_dir = os.path.dirname(__file__)
        key_path = os.path.join(module_dir, 'key_gen.pub')
        public_key = open(key_path).read()
        try:
            payload = jwt.decode(request_token, public_key, algorithms=['RS256'])
        except jwt.exceptions.InvalidTokenError:
            return Response(data='Invalid token error', status=status.HTTP_400_BAD_REQUEST)
        
        # generate new content and its keys
        contentId = self.__generateContentId()
        new_content = ContentModel(content_id = contentId, content_name=payload['name'])
        new_content.save()
        keys = self.__generateKeys(payload['num'])
        for i in range(payload['num']):
            new_key = KeyModel(key_id=keys[i]['kid'], key=keys[i]['k'], content=new_content)
            new_key.save()
        response = {'content_id':contentId, 'name': payload['name'], 'keys': keys}
        return Response(data=response, status=status.HTTP_200_OK)
    
    def __randomHexString(self, len=32):
        return binascii.b2a_hex(os.urandom(16)).decode('utf-8')
    
    def __base64encode(self, s):
        b = hexdump.dehex(s)
        return base64.urlsafe_b64encode(b).decode('utf-8').rstrip('=')

    def __generateContentId(self):
        contentId = ''
        while True:
            contentId = self.__base64encode(self.__randomHexString())
            try:
                ContentModel.objects.get(pk=contentId)
                continue
            except ContentModel.DoesNotExist:
                break
        return contentId

    def __generateKeys(self, num):
        keys = []
        while len(keys)<num:
            keyid = self.__base64encode(self.__randomHexString())
            try:
                KeyModel.objects.get(pk=keyid)
                continue
            except KeyModel.DoesNotExist:
                key = self.__base64encode(self.__randomHexString())
                keys.append({'k': key, 'kid': keyid})
        return keys