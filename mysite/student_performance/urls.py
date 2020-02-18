from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^store/$', views.storePerformancePoints.as_view(), name='storePerformancePoints'),
    url(r'^getmyperformance/(?P<username>[a-zA-Z0-9_.-]+)/$', views.getPerformance.as_view(), name='getPerformance'),
    url(r'^getkarampoints/$', views.getKaramPoints.as_view(), name='getKaramPoints'),
]


