from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^hello$', views.hello, name = 'hello'),
    url(r'^updateprofile$', views.updateprofile, name='updateprofile'),
    url(r'^completeprofile$', views.complete_profile, name='complete_profile'),
    url(r'^verify_profile$', views.verify_profile, name='verify_profile'),
    url(r'^check_if_user_exists$', views.check_if_user_exists, name='check_if_user_exists'),
    url(r'^announcements$', views.announcements, name='announcements'),
    url(r'^userlist/$', views.userlist, name='userlist'),
    url(r'^user_data/$', views.user_data, name='user_data'),
    url(r'^user_data_updated/$', views.user_data_updated, name='user_data_updated'),
    url(r'^getNameFromUsername/$', views.getNameFromUsername, name='getNameFromUsername'),
    url(r'^get_class_info/$', views.get_class_info, name='get_class_info'),
    url(r'^update_parents_details$', views.update_parents_details, name='update_parents_details'),
    url(r'^profile_progress/$', views.profile_progress, name='profile_progress'),
    url(r'^announcements_updated$', views.announcements_updated, name='announcements_updated'),
    url(r'^createCourse$', views.createCourse, name='createCourse'),
    url(r'^whatsnew$', views.whatsnew, name='whatsnew'),
    url(r'^whatsnew_shyam_sharma$', views.whatsnew_shyam_sharma, name='whatsnew_shyam_sharma'),
    url(r'^whatsnew_the_optimist$', views.whatsnew_the_optimist, name='whatsnew_the_optimist'),
    url(r'^whatsnew_spsharma$', views.whatsnew_spsharma, name='whatsnew_spsharma'),
    url(r'^whatsnew_all/(?P<collection_name>[a-zA-Z0-9_.-]+)/$', views.whatsnew_all, name='whatsnew_all'),
]

