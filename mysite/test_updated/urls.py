from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^hello$', views.hello, name = 'hello'),
    url(r'^test/$', views.test_function, name='test'),
    url(r'^newsubmission$', views.newsubmission, name='newsubmission'),
    url(r'^newtestsubmission$', views.newTestSubmission, name='newTestSubmission'),
    url(r'^exams_list$', views.exams_list, name='exams_list'),
    url(r'^get_test_data$', views.get_test_data, name='get_test_data'),
    url(r'^get_chapterwise_test_data$', views.get_chapterwise_test_data, name='get_chapterwise_test_data'),
    url(r'^get_topic_list$', views.get_topic_list, name='get_topic_list'),
    url(r'^save_test_performance$', views.save_test_performance, name='save_test_performance'),
    url(r'^save_test_performance_updated$', views.save_test_performance_updated, name='save_test_performance_updated'),
    url(r'^save_test_data$', views.save_test_data, name='save_test_data'),
    url(r'^view_attempted_test/(?P<test_id>[a-zA-Z0-9_.-]+)/$', views.view_attempted_test, name='view_attempted_test'),
]

