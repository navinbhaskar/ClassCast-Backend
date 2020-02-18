from django.db import models
import sys
sys.path.append("..")
from mysite.users.models import user_info
from mysite.teachers.models import teacher_info
from datetime import datetime, timedelta
import random
import string

class course_details(models.Model):
    course_id = models.CharField(max_length=25, primary_key=True)
    course_name = models.CharField(max_length=40)
    teacher=models.ForeignKey(teacher_info, on_delete=models.CASCADE)
    course_details = models.CharField(max_length=2000, blank =True)
    books_available=models.BooleanField(default=False)
    amount = models.FloatField(null=True, blank=True, default=0.00)
    amount_course_plus_books = models.FloatField(null=True, blank=True, default=0.00)
    amount_only_books = models.FloatField(null=True, blank=True, default=0.00)
    access_token_only=models.BooleanField(default=False)
    thumbnail = models.CharField(max_length=1000, blank =True)

    def __str__(self):
        return u'%s-%s- %s %s' % (str(self.course_id), str(self.course_name), str(self.teacher.firstname), str(self.teacher.lastname))


class chapter_details(models.Model):
    chapter_id = models.CharField(max_length=25, primary_key=True)
    chapter_name = models.CharField(max_length=100, blank =True)
    chapter_details = models.CharField(max_length=500, blank =True)
    course=models.ForeignKey(course_details, on_delete=models.CASCADE)
    thumbnail = models.CharField(max_length=1000, blank =True)

    def __str__(self):
        return u'%s-%s' % (str(self.chapter_id), str(self.course.course_id))

class test_series_details(models.Model):
    test_series_id = models.CharField(max_length=25, primary_key=True)
    test_series_name = models.CharField(max_length=40)
    teacher=models.ForeignKey(teacher_info, on_delete=models.CASCADE)
    test_series_details = models.CharField(max_length=2000, blank =True)
    amount = models.FloatField(null=True, blank=True, default=0.00)
    access_token_only=models.BooleanField(default=False)
    thumbnail = models.CharField(max_length=1000, blank=True)
    thumbnail_free_test = models.CharField(max_length=1000, blank=True)
    paid_test_available=models.BooleanField(default=True)
    free_test_available=models.BooleanField(default=True)

    def __str__(self):
        return u'%s-%s- %s %s' % (str(self.test_series_id), str(self.test_series_name), str(self.teacher.firstname), str(self.teacher.lastname))


class test_details(models.Model):
    test_id = models.CharField(max_length=25, primary_key=True)
    test_name = models.CharField(max_length=100, blank =True)
    test_details = models.CharField(max_length=500, blank =True)
    test_series=models.ForeignKey(test_series_details, on_delete=models.CASCADE)
    thumbnail = models.CharField(max_length=1000, blank =True)
    free = models.BooleanField(default=False)
    no_of_questions = models.IntegerField(default=0)
    pos_marks = models.FloatField(default=1)
    neg_marks = models.FloatField(default=0.25)
    negative_marking = models.BooleanField(default=False)
    assignment = models.BooleanField(default=False)
    duration = models.IntegerField(default=1800)
    timestamp = models.DateTimeField(default=datetime.now)
    start_date = models.DateTimeField(default=datetime.now)
    end_date = models.DateTimeField(default= datetime.now() + timedelta(days=2*365))

    def __str__(self):
        return u'%s-%s' % (str(self.test_id), str(self.test_series.test_series_id))


class test_series_videos(models.Model):
    course_id = models.CharField(max_length=25, primary_key=True)
    test_series=models.ForeignKey(test_series_details, on_delete=models.CASCADE)
    free = models.BooleanField(default=False)

    def __str__(self):
        return u'%s-%s' % (str(self.course_id), str(self.test_series.test_series_id))


class student_course_interactions(models.Model):
    PAYMENT = 'Payment'
    TOKEN = 'Token'
    STATUS = [
    	(PAYMENT, ('Payment')),
        (TOKEN, ('Token'))
    ]

    COURSE = 'course'
    COURSE_PLUS_BOOKS = 'course_plus_books'
    ONLY_BOOKS = 'only_books'
    PACKAGE = [
        (COURSE, ('course')),
        (COURSE_PLUS_BOOKS, ('course_plus_books')),
        (ONLY_BOOKS, ('only_books'))
    ]

    student=models.ForeignKey(user_info, on_delete=models.CASCADE, blank=True, null=True)
    course=models.ForeignKey(course_details, null = True, on_delete=models.SET_NULL)
    enrollment_method=models.CharField( max_length=32, choices=STATUS, default=TOKEN,)
    payement_mode = models.CharField(max_length=40, blank=True)
    payment_id = models.CharField(max_length=100, blank=True)
    timestamp = models.DateTimeField(default=datetime.now, blank=True)
    enrollment_status = models.CharField(max_length=50, blank=True)
    course_package = models.CharField( max_length=50, choices=PACKAGE, default=COURSE,)
    package = models.CharField(max_length=50, blank=True)

    def __str__(self):
   	    return u'%s %s - %s' % (str(self.student.firstname), str(self.student.lastname), str(self.payement_mode))

class student_test_interactions(models.Model):

    PAYMENT = 'Payment'
    TOKEN = 'Token'
    STATUS = [
        (PAYMENT, ('Payment')),
        (TOKEN, ('Token'))
    ]

    student=models.ForeignKey(user_info, on_delete=models.CASCADE, blank=True, null=True)
    test_series=models.ForeignKey(test_series_details, null = True, on_delete=models.SET_NULL)
    enrollment_method=models.CharField( max_length=32, choices=STATUS, default=TOKEN,)
    payement_mode = models.CharField(max_length=40, blank=True)
    payment_id = models.CharField(max_length=100, blank=True)
    timestamp = models.DateTimeField(default=datetime.now, blank=True)
    enrollment_status = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return u'%s %s - %s' % (str(self.student.firstname), str(self.student.lastname), str(self.payement_mode))


class course_package(models.Model):
    teacher=models.ForeignKey(teacher_info, on_delete=models.CASCADE, blank=True, null=True)
    package_id = models.CharField(max_length=20, primary_key=True)
    package_name = models.CharField(max_length=100, blank =False)
    course_on_display = models.ForeignKey(course_details, null = True, on_delete=models.SET_NULL)
    details = models.CharField(max_length=500, blank =True)
    thumbnail = models.CharField(max_length=1000, blank =True)

    def __str__(self):
        return u'%s - %s' % (str(self.package_id), str(self.package_name))

class package_details(models.Model):
    selected_package=models.ForeignKey(course_package, on_delete=models.CASCADE, blank=True, null=True)
    course=models.ForeignKey(course_details, null = True, on_delete=models.SET_NULL)
    details = models.CharField(max_length=500, blank =True)
    amount = models.FloatField(null=True, blank=True, default=0.00)

    def __str__(self):
        return u'%s - %s' % (str(self.selected_package.package_id), str(self.course.course_id))


class access_code_coursewise(models.Model):
    course=models.ForeignKey(course_details, on_delete=models.CASCADE)
    access_code = models.CharField(max_length=10000,blank=False)
    student=models.ForeignKey(user_info, on_delete=models.CASCADE, blank=True, null=True)
    batch_id=models.CharField(max_length=60, blank=True)
    expired=models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=datetime.now, blank=True)
    def __str__(self):
        return u'%s-%s-%s-%s' % (str(self.course.course_id), str(self.access_code), str(self.expired), str(self.batch_id))


class course_test_series_list(models.Model):
    course=models.ForeignKey(course_details, on_delete=models.CASCADE)
    test_series=models.ForeignKey(test_series_details, on_delete=models.CASCADE)

    def __str__(self):
        return u'%s-%s' % (str(self.test_series.test_series_name), str(self.course.course_id))

class course_package_details(models.Model):
    package_id = models.CharField(max_length=20, default=''.join(random.choices(string.ascii_uppercase + string.digits, k=6)))
    package_name = models.CharField(max_length=100, blank =True)
    package_details = models.CharField(max_length=500, blank =True)
    course=models.ForeignKey(course_details, on_delete=models.CASCADE)
    amount = models.FloatField(null=True, blank=True, default=0.00)

    def __str__(self):
        return u'%s-%s' % (str(self.package_name), str(self.course.course_id))


class access_code_test_series_wise(models.Model):
    test_series=models.ForeignKey(test_series_details, on_delete=models.CASCADE)
    access_code = models.CharField(max_length=10000,blank=False)
    student=models.ForeignKey(user_info, on_delete=models.CASCADE, blank=True, null=True)
    batch_id=models.CharField(max_length=60, blank=True)
    expired=models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=datetime.now, blank=True)
    def __str__(self):
        return u'%s-%s-%s-%s' % (str(self.test_series.test_series_id), str(self.access_code), str(self.expired), str(self.batch_id))


class access_code_premium(models.Model):
    teacher=models.ForeignKey(teacher_info, on_delete=models.CASCADE)
    access_code = models.CharField(max_length=10000,blank=False)
    student=models.ForeignKey(user_info, on_delete=models.CASCADE, blank=True, null=True)
    batch_id=models.CharField(max_length=60, blank=True)
    expired=models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=datetime.now, blank=True)
    def __str__(self):
        return u'%s %s-%s-%s-%s' % (str(self.teacher.firstname), str(self.teacher.lastname), str(self.access_code), str(self.expired), str(self.batch_id))