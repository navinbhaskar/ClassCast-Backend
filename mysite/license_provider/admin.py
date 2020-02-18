from django.contrib import admin
from .models import KeyModel
from .models import ContentModel 
# Register your models here.
admin.site.register(KeyModel)
admin.site.register(ContentModel)