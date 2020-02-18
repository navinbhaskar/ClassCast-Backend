from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^generateaccesscode/(?P<teacherid>[a-zA-Z0-9_.-]+)/(?P<batch_id>[a-zA-Z0-9_.-]+)/(?P<number>[a-zA-Z0-9_.-]+)/$', views.generateAccessCode.as_view(), name='generateAccessCode'),
    url(r'^enroll/$', views.enrollment_from_token.as_view(), name='enrollment_from_token'),
    url(r'^enrollment_from_token_white_label/$', views.enrollment_from_token_white_label.as_view(), name='enrollment_from_token_white_label'),
    url(r'^access_code_data/$', views.access_code_data, name='access_code_data'),
]

