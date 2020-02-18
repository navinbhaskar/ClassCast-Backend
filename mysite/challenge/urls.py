from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^hello$', views.hello, name = 'hello'),
    url(r'^phonenumber$', views.phonenumber, name='phonenumber'),
    url(r'^createChallenge$', views.createChallenge, name='createChallenge'),
    url(r'^updated_createChallenge$', views.updated_createChallenge, name='updated_createChallenge'),
    url(r'^fetchchallengequestions/(?P<challengeid>[a-zA-Z0-9_.-]+)/$', views.fetchChallengequestions, name='fetchChallengequestions'),
    url(r'^updateChallengeRequest$', views.updateChallengeRequest, name='updateChallengeRequest'),
    url(r'^getchallengedata/(?P<challengeid>[a-zA-Z0-9_.-]+)/$', views.getChallengeData, name='getChallengeData'),
    url(r'^submitchallengequestions$', views.submitChallengeQuestions, name='submitChallengeQuestions'),
]

