from django.contrib import admin
from . models import teacher_account, teacher_batch_data, class_attendance_data, fcm_token_teacher, teacher_credentials

admin.site.register(teacher_account)
admin.site.register(teacher_batch_data)
admin.site.register(class_attendance_data)
admin.site.register(fcm_token_teacher)
admin.site.register(teacher_credentials)


