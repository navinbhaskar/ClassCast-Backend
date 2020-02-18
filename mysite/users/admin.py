from django.contrib import admin
from . models import user_info, exam_info, parents_details
from django.contrib.auth.models import User, Group


class user_infoAdmin(admin.ModelAdmin):

    search_fields = ('username','email', 'firstname', 'lastname', 'phone_number')

admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.register(user_info, user_infoAdmin)
admin.site.register(exam_info)
admin.site.register(parents_details)

