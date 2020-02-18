from django.contrib import admin
from . models import fcm_token

class fcm_tokenAdmin(admin.ModelAdmin):

    search_fields = ('student__username',)

admin.site.register(fcm_token, fcm_tokenAdmin)
