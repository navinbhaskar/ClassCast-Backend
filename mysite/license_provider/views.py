from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import KeyModel

class LicenseProvider(APIView):
    def get(self, request, format=None):
        q_kids = [k[0] for k in request.query_params.items()]
        q_keys = [KeyModel.objects.values_list('key', flat=True).get(pk=kid) for kid in q_kids]
        keys = []
        for i in range(len(q_keys)):
            keys.append({'kty':'oct', 'k':q_keys[i], 'kid':q_kids[i]})
        license_response = {"keys":keys, "type":"temporary"}
        return Response(data=license_response, status=status.HTTP_200_OK)
    
    def post(self, request, format=None):
        print(request.data['kids'])
        key = KeyModel.objects.get(pk=request.data['kids'][0])
        content = key.content
        keys = content.keys.all()
        response = {}
        response['content_id'] = content.content_id
        response['name'] = content.content_name
        response['keys'] = []
        response['type'] = request.data['type']
        for k in keys:
            response["keys"].append({'kty':'oct', 'k':k.key, 'kid':k.key_id})
        return Response(data=response, status=status.HTTP_200_OK)
