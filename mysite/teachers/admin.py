from django.contrib import admin
from . models import teacher_info, teacher_student_interaction, course_enrollment, access_code

class teacher_infoAdmin(admin.ModelAdmin):

    search_fields = ('teacher_id','coaching_name', 'firstname', 'lastname')

class access_codeAdmin(admin.ModelAdmin):

    search_fields = ('access_code', 'batch_id', 'student__username')

class teacher_student_interactionAdmin(admin.ModelAdmin):

    search_fields = ('teacher__teacher_id', 'student__username')

admin.site.register(teacher_info, teacher_infoAdmin)
admin.site.register(teacher_student_interaction, teacher_student_interactionAdmin)
admin.site.register(course_enrollment)
admin.site.register(access_code, access_codeAdmin)


