from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^hello$', views.hello, name = 'hello'),
    url(r'^get_chapterwise_gym_data$', views.get_chapterwise_gym_data, name='get_chapterwise_gym_data'),
    url(r'^get_gym_data$', views.get_gym_data, name='get_gym_data'),
    url(r'^new_gym/$', views.new_gym_function, name='new_gym'),
]

