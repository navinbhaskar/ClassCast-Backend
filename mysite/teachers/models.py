from django.db import models
import sys
sys.path.append("..")
from mysite.users.models import user_info
#from mysite.white_label.models import course_details
from datetime import datetime

class teacher_info(models.Model):
    gender_choices = [('1', 'Male'), ('2', 'Female')]
    
    teacher_id = models.CharField(primary_key=True, max_length=40,)
    firstname = models.CharField(max_length=40, default=0)
    lastname = models.CharField(max_length=40, blank =True)
    gender = models.CharField(max_length=9, choices=gender_choices, default='1')
    subject = models.CharField(max_length=40,default=0)
    classes = models.CharField(max_length=40,default=0)
    photo = models.CharField(max_length=100, blank =True)
    coaching_name = models.CharField(max_length=40, blank =True)
    qualification = models.CharField(max_length=250, blank =True)
    area = models.CharField(max_length=40,default=0)
    pincode = models.CharField(max_length=10, blank =True)
    goal = models.CharField(max_length=50, blank =True)
    rating = models.IntegerField(blank =True)
    about = models.CharField(max_length=250, blank =True)
    courses = models.CharField(max_length=5000,blank=True)
    batches = models.CharField(max_length=500,blank=True)
    classcast_select=models.BooleanField(default=False)
    def __str__(self):
        return u'%s-%s-%s' % (str(self.firstname), str(self.subject), str(self.area))


class access_code(models.Model):
    teacher=models.ForeignKey(teacher_info, on_delete=models.CASCADE)
    access_code = models.CharField(max_length=10000,blank=False)
    student=models.ForeignKey(user_info, on_delete=models.CASCADE, blank=True, null=True)
    batch_id=models.CharField(max_length=60, blank=True)
    expired=models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=datetime.now, blank=True)
    def __str__(self):
        return u'%s-%s-%s-%s' % (str(self.teacher.firstname), str(self.teacher.lastname), str(self.expired), str(self.batch_id))


class teacher_student_interaction(models.Model):
    student=models.ForeignKey(user_info, on_delete=models.CASCADE)
    teacher=models.ForeignKey(teacher_info, on_delete=models.CASCADE)
    is_approved=models.BooleanField(default=0)
    is_active=models.BooleanField(default=0)
    batch_id = models.CharField(max_length=60, blank=True)
    date_joined=models.DateTimeField(auto_now_add=True)
    date_left=models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('student', 'teacher',)

    def __str__(self):
        return u'%s-%s-%s-%s-%s' % (str(self.student.username), str(self.teacher.firstname), str(self.is_approved), str(self.batch_id), str(self.date_joined))



class course_enrollment(models.Model):
    student=models.ForeignKey(user_info, on_delete=models.CASCADE)
    course_id=models.CharField(max_length=60, blank=False)
    is_enrolled=models.BooleanField(default=0)
    date_joined = models.DateTimeField(auto_now_add=True)
    batch = models.ForeignKey(teacher_student_interaction, on_delete=models.CASCADE)
    def __str__(self):
        return u'%s-%s-%s' % (str(self.student.username), str(self.course_id), str(self.date_joined))




