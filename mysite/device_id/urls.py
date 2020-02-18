from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^get_device_id/$', views.get_device_id.as_view(), name='get_device_id'),
	url(r'^save_device_id/$', views.save_device_id.as_view(), name='save_device_id'),
	url(r'^get_device_id_updated/$', views.get_device_id_updated.as_view(), name='get_device_id_updated'),
]

