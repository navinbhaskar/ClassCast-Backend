"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from graphene_django.views import GraphQLView
from mysite.license_provider import views 
from mysite.key_generator import views as keyviews

admin.site.site_header = "ClassCast"
admin.site.site_title = "ClassCast Admin Portal"
admin.site.index_title = "Welcome to ClassCast"

urlpatterns = [
    path('', admin.site.urls),
    path('admin/', admin.site.urls),
    path('gym/', include('mysite.gym_updated.urls')),
    path('users/', include('mysite.users.urls')),
    path('teachers/', include('mysite.teachers.urls')),
    path('accesstoken/', include('mysite.generate_access_code.urls')),
    path('graphql', GraphQLView.as_view(graphiql=True)),
    path('coursedata/', include('mysite.course_data.urls')),
    path('challenge_updated/', include('mysite.challenge_updated.urls')),
    path('performance/', include('mysite.student_performance.urls')),
    path('test/', include('mysite.test.urls')),
    path('test_updated/', include('mysite.test_updated.urls')),
    path('challenge/', include('mysite.challenge.urls')),
    path('token/', include('mysite.fcm_token.urls')),
    path('deviceid/', include('mysite.device_id.urls')),
    path('teachersapp/', include('mysite.teachers_app.urls')),
    path('white_label/', include('mysite.white_label.urls')),
    path('getLicense/', views.LicenseProvider.as_view()),
    path('generateContentAndKeys/', keyviews.KeyGenerator.as_view())
]
