from django.db import models
import datetime
import sys
sys.path.append("..")
from mysite.teachers.models import teacher_info
from mysite.users.models import user_info

class teacher_account(models.Model):
    username = models.CharField(primary_key=True, max_length=100)
    teacher=models.ForeignKey(teacher_info, on_delete=models.CASCADE)
    Type = models.CharField(max_length=40, default=0)

    def __str__(self):
        return u'%s-%s' % (str(self.username), str(self.Type))

class teacher_batch_data(models.Model):
	standard_choices = [('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5','5'),('6', '6'),('7', '7'), ('8', '8'), ('9', '9'), ('10', '10'), ('11','11'),('12', '12'),('13','13'),('14','SSC'),('15','Bank PO'),('16','Railways'),('17','Bank Clerk'),('18','')]
	teacher=models.ForeignKey(teacher_info, on_delete=models.CASCADE)
	batch_id = models.CharField(max_length=40, default='Batch-1')
	standard = models.CharField(max_length=5, choices=standard_choices, default='18')
	sunday=models.BooleanField(default=False)
	monday=models.BooleanField(default=False)
	tuesday=models.BooleanField(default=False)
	wednesday=models.BooleanField(default=False)
	thursday=models.BooleanField(default=False)
	friday=models.BooleanField(default=False)
	saturday=models.BooleanField(default=False)
	class_start_timing = models.TimeField(default=datetime.time(00, 00))
	class_end_timing = models.TimeField(default=datetime.time(00, 00))
	class Meta:
		unique_together = ('teacher','batch_id', 'standard',)

	def __str__(self):
		return u'%s-%s-%s-%s' % (str(self.teacher.firstname), str(self.teacher.lastname), str(self.batch_id), str(self.standard))


class class_attendance_data(models.Model):
	student=models.ForeignKey(user_info, on_delete=models.CASCADE, blank=True, null=True)
	batch=models.ForeignKey(teacher_batch_data, on_delete=models.CASCADE)
	class_attended=models.BooleanField(default=False)
	timestamp = models.DateField(default=datetime.date.today(), blank=True)

	class Meta:
		unique_together = ('student','batch', 'timestamp',)

	def __str__(self):
		return u'%s-%s-%s-%s-%s-%s' % (str(self.student.firstname), str(self.student.lastname), str(self.batch.teacher.firstname), str(self.batch.teacher.lastname), str(self.class_attended), str(self.timestamp))


class fcm_token_teacher(models.Model):
    teacher=models.ForeignKey(teacher_account, on_delete=models.CASCADE)
    fcmToken = models.CharField(max_length=5000, blank =True)
    def __str__(self):
        return u'%s' % (str(self.teacher.username))

class teacher_credentials(models.Model):
    username = models.CharField(primary_key=True, max_length=100)
    teacher=models.ForeignKey(teacher_info, on_delete=models.CASCADE)
    password = models.CharField(max_length=100, default=0)

    def __str__(self):
        return u'%s' % (str(self.username))