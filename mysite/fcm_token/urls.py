from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^get_fcm_token/(?P<username>[a-zA-Z0-9_.-]+)/$', views.get_fcm_token.as_view(), name='get_fcm_token'),
	url(r'^get_multiple_fcm_token$', views.get_multiple_fcm_token, name='get_multiple_fcm_token'),
	url(r'^get_multiple_fcm_token_with_username$', views.get_multiple_fcm_token_with_username, name='get_multiple_fcm_token_with_username'),
	url(r'^save_fcm_token/$', views.save_fcm_token.as_view(), name='save_fcm_token'),
]
