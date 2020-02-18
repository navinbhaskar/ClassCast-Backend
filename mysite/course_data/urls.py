from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^fetchChapterBlocks/(?P<course_id>[a-zA-Z0-9_.-]+)/(?P<chapter_id>[a-zA-Z0-9_.-]+)/$', views.fetchChapterBlocks.as_view(), name='fetchChapterBlocks'),
    url(r'^courseblocks/(?P<courseid>[a-zA-Z0-9_.-]+)/$', views.fetchCourseBlocks.as_view(), name='fetchCourseBlocks'),
    url(r'^chapterlist/(?P<standard>[a-zA-Z0-9_.-]+)/(?P<subject>[a-zA-Z0-9_.-]+)/$', views.chapterlist.as_view(), name = 'chapterlist'),
    url(r'^generateSignedUrl$', views.generateSignedUrl, name='generateSignedUrl'),
    url(r'^fetchassignmentquestions$', views.fetchAssignmentQuestions, name='fetchAssignmentQuestions'),
    url(r'^storestudentblockinteractions$', views.storeStudentBlockInteractions, name='storeStudentBlockInteractions'),
    url(r'^storepointsfromcourseblocks$', views.storeScoreFromCourseBlocks, name='storeScoreFromCourseBlocks'),
    url(r'^updated_chapterlist/(?P<subject>[a-zA-Z0-9_.-]+)/$', views.updated_chapterlist.as_view(), name = 'updated_chapterlist'),
    url(r'^uploadQuestions/$', views.uploadQuestions, name = 'uploadQuestions'),
    url(r'^testGoalAndSubjectList/$', views.testGoalAndSubjectList, name = 'testGoalAndSubjectList'),
    url(r'^update_chapterdata$', views.update_chapterdata, name='update_chapterdata'),
    url(r'^myTests/(?P<teacher_id>[a-zA-Z0-9_.-]+)/$', views.myTests.as_view(), name = 'myTests'),
    url(r'^store_discussion_data$', views.store_discussion_data, name='store_discussion_data'),
    url(r'^store_block_discussion_data$', views.store_block_discussion_data, name='store_block_discussion_data'),
    #url(r'^generateSignedUrl/(?P<bucketname>[a-zA-Z0-9_.-]+)/(?P<filename>[a-zA-Z0-9_.-]+)/$', views.generateSignedUrl.as_view(), name = 'generateSignedUrl'),
]

