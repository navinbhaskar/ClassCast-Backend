from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^myteachers/$', views.MyTeachersList.as_view(), name='MyTeachersList'),
    url(r'^allteachers/(?P<subject>[a-zA-Z0-9_.-]+)/(?P<goal>[a-zA-Z0-9_.-]+)/$', views.AllTeachersList.as_view(), name='AllTeachersList'),
    url(r'^teacherlist/$', views.StudentRequest.as_view(), name='StudentRequest'),
    url(r'^teachercoursedata/(?P<teacherid>[a-zA-Z0-9_.-]+)/$', views.teachercoursedata.as_view(), name='teachercoursedata'),
    url(r'^teachercoursedatanew/(?P<teacherid>[a-zA-Z0-9_.-]+)/$', views.teachercoursedatanew.as_view(), name='teachercoursedatanew'),
    url(r'^availableTeachers/(?P<username>[a-zA-Z0-9_.-]+)/$', views.availableTeachers.as_view(), name='availableTeachers'),
    url(r'^getpercentagecompletion/(?P<courseid>[a-zA-Z0-9_.-]+)/$', views.getpercentagecompletion.as_view(), name='getpercentagecompletion'),
    url(r'^getCompletionBlocks/(?P<courseid>[a-zA-Z0-9_.-]+)/$', views.getCompletionBlocks.as_view(), name='getCompletionBlocks'),
    url(r'^getRecentCompletedBlocks/$', views.getRecentCompletedBlocks.as_view(), name='getRecentCompletedBlocks'),
    url(r'^recommendedTestData/$', views.recommendedTestData.as_view(), name='recommendedTestData'),
    url(r'^idToTeacherName/(?P<teacher_id>[a-zA-Z0-9_.-]+)/$', views.idToTeacherName.as_view(), name='idToTeacherName'),
    url(r'^idToTeacherDetails/(?P<teacher_id>[a-zA-Z0-9_.-]+)/$', views.idToTeacherDetails.as_view(), name='idToTeacherDetails'),
    url(r'^MyCrashCourseList/$', views.MyCrashCourseList.as_view(), name='MyCrashCourseList'),
    url(r'^enroll_student/(?P<teacher_id>[a-zA-Z0-9_.-]+)/(?P<course_id>[a-zA-Z0-9_.-]+)/$', views.enroll_student.as_view(), name='enroll_student'),
    url(r'^add_crashcourse_enrollment/$', views.add_crashcourse_enrollment.as_view(), name='add_crashcourse_enrollment'),
]



