from django.db import models

# Create your models here.
class ContentModel(models.Model):
    content_id = models.CharField(max_length=22, primary_key=True)
    content_name = models.TextField()
    active = models.BooleanField(default=False)

class KeyModel(models.Model):
    key_id = models.CharField(max_length=22, primary_key=True)
    key = models.CharField(max_length=22, blank=False)
    content = models.ForeignKey(ContentModel, on_delete=models.CASCADE, related_name="keys")