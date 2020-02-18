from django.db import models
import sys
sys.path.append("..")
from mysite.users.models import user_info

class fcm_token(models.Model):
    student=models.ForeignKey(user_info, on_delete=models.CASCADE)
    fcmToken = models.CharField(max_length=5000, blank =True)
    def __str__(self):
        return u'%s' % (str(self.student.username))