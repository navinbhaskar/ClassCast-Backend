from django.contrib import admin
from . models import device_id

class device_idAdmin(admin.ModelAdmin):

    search_fields = ('student__username',)

admin.site.register(device_id, device_idAdmin)
