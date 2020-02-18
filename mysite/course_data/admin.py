from django.contrib import admin
from . models import chapter, topics, questionSagar, Classcast_test_submission, student_topic_interaction, student_block_interactions, classcast_question, question, questions, exams, exams_package, test_sections, chapter_updated, live_courses, crashcourse_enrollment

class questionAdmin(admin.ModelAdmin):
    search_fields = ('xblock_id','question', 'chapter', 'subject')

class student_block_interactionsAdmin(admin.ModelAdmin):
    search_fields = ('course_id','block', 'student__username')

admin.site.register(chapter)
admin.site.register(topics)
admin.site.register(questionSagar)
admin.site.register(Classcast_test_submission)
admin.site.register(student_topic_interaction)
admin.site.register(student_block_interactions, student_block_interactionsAdmin)
admin.site.register(classcast_question)
admin.site.register(question, questionAdmin)
admin.site.register(questions)
admin.site.register(exams)
admin.site.register(exams_package)
admin.site.register(test_sections)
admin.site.register(chapter_updated)
admin.site.register(live_courses)
admin.site.register(crashcourse_enrollment)