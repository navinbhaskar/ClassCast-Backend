from django.contrib import admin
from . models import course_details, chapter_details, student_course_interactions, access_code_coursewise, test_series_details, test_details, student_test_interactions, test_series_videos, course_test_series_list, course_package_details, access_code_test_series_wise, access_code_premium

class chapter_detailsAdmin(admin.ModelAdmin):

    search_fields = ('course__course_id', 'chapter_id')

class access_code_coursewiseAdmin(admin.ModelAdmin):

    search_fields = ('student__username', 'access_code', 'course__course_id')

class access_code_test_series_wiseAdmin(admin.ModelAdmin):

    search_fields = ('student__username', 'access_code', 'course__course_id')

admin.site.register(course_details)
admin.site.register(chapter_details, chapter_detailsAdmin)
admin.site.register(student_course_interactions)
admin.site.register(access_code_coursewise, access_code_coursewiseAdmin)
admin.site.register(test_series_details)
admin.site.register(test_details)
admin.site.register(student_test_interactions)
admin.site.register(test_series_videos)
admin.site.register(course_test_series_list)
admin.site.register(course_package_details)
admin.site.register(access_code_test_series_wise, access_code_test_series_wiseAdmin)
admin.site.register(access_code_premium)