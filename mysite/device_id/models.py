from django.db import models
import sys
sys.path.append("..")
from mysite.users.models import user_info

class device_id(models.Model):
    student=models.ForeignKey(user_info, on_delete=models.CASCADE)
    device_id = models.CharField(max_length=100, blank =True)
    def __str__(self):
        return u'%s' % (str(self.student.username))