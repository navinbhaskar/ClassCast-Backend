from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^hello$', views.hello, name = 'hello'),
    url(r'^gym/$', views.gym_function, name='gym'),
    url(r'^new_gym/$', views.new_gym_function, name='new_gym'),
    url(r'^updated_gym_function/$', views.updated_gym_function, name='updated_gym_function'),
]


