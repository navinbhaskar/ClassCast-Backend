from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^hello$', views.hello, name = 'hello'),
    url(r'^test/$', views.test_function, name='test'),
    url(r'^newtest/$', views.new_test_function, name='newtest'),
    url(r'^newsubmission$', views.newsubmission, name='newsubmission'),
    url(r'^updated_test_function/$', views.updated_test_function, name='updated_test_function'),
    url(r'^newtestsubmission$', views.newTestSubmission, name='newTestSubmission')
]

