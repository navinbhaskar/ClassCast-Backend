from django.db import models
import sys
sys.path.append("..")
from mysite.users.models import user_info, exam_info
from mysite.teachers.models import teacher_info
from datetime import datetime

class chapter(models.Model):
    id = models.IntegerField(primary_key=True)
    standard =models.IntegerField()
    subject=models.CharField(max_length=50)
    chapter=models.CharField(max_length=255)

    class Meta:
            unique_together = (("standard","subject","chapter"),)

    def __str__(self):
            return str(self.standard) + ":" + self.subject + ":" + self.chapter 

class topics(models.Model):
    chapter=models.ForeignKey(chapter, on_delete=models.CASCADE)
    topic_name=models.CharField(max_length=255)
    topic_id=models.IntegerField(primary_key=True)

    def __str__(self):
            return str(self.chapter) + ":"+ self.topic_name

class questionSagar(models.Model):
    xblock_id = models.CharField(max_length=100, blank=False, unique=True, primary_key=True)
    goal = models.CharField(max_length=40, blank=False)
    standard = models.IntegerField(blank=True)
    subject = models.CharField(max_length=20, blank=True)
    chapter = models.CharField(max_length=50, blank=True)
    topic = models.CharField(max_length=100, blank=True)
    questionType = models.CharField(max_length=10, blank=True)
    difficulty = models.IntegerField(blank=True)
    
    class Meta:
        db_table = 'questionSagar'     

class student_topic_interaction(models.Model):
    student = models.ForeignKey(user_info, on_delete=models.CASCADE)
    xblock = models.ForeignKey(questionSagar, on_delete=models.CASCADE)
    difficulty = models.IntegerField()
    topic = models.CharField(max_length=100, blank=True)
    attempted = models.IntegerField()
    correctly_attempted = models.IntegerField()
    num_skips = models.IntegerField()
    time_taken = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    attempted_in_test = models.BooleanField()
    attempted_in_gym = models.BooleanField()

    class Meta:
        db_table = 'student_topic_interaction'

    def __str__(self):
        return u'%s %s' % (str(self.student), str(self.xblock))


class Classcast_test_submission(models.Model):
    student = models.ForeignKey(user_info, on_delete=models.CASCADE)
    chapter = models.ForeignKey(chapter, on_delete=models.CASCADE)
    score = models.IntegerField()
    n_questions = models.IntegerField(default='0', blank=True)
    time_taken = models.FloatField()
    timestamp = models.DateTimeField(default=datetime.now, blank=True)

    class Meta:
        db_table = 'classcast_test_submissions'

    def __str__(self):
        return u'%s %s' % (str(self.student), str(self.chapter))


class student_block_interactions(models.Model):
    student = models.ForeignKey(user_info, on_delete=models.CASCADE)
    course_id=models.CharField(max_length=15, default="None")
    block=models.CharField(max_length=300, blank=False)
    timestamp = models.DateTimeField(default=datetime.now, blank=True)
    rating = models.IntegerField(default='0')
    review=models.CharField(max_length=1000, default="")
    class Meta:
        db_table = 'student_block_interactions'

    def __str__(self):
        return u'%s %s' % (str(self.student), str(self.course_id))

class classcast_question(models.Model):
    xblock_id = models.CharField(max_length=100, blank=False, unique=True, primary_key=True)
    goal = models.CharField(max_length=40, blank=True)
    standard = models.IntegerField(blank=True, default=0)
    subject = models.CharField(max_length=20, blank=True)
    chapter = models.CharField(max_length=50, blank=True)
    topic = models.CharField(max_length=100, blank=True)
    difficulty = models.IntegerField(blank=True, default=1)
    marks = models.IntegerField(blank=True, default=3)
    negativeMarks = models.IntegerField(blank=True, default=-1)
    questionType = models.CharField(max_length=20, blank=True)
    tags=models.CharField(max_length=1000, default = None)
    question=models.CharField(max_length=5000, default = None)
    option1=models.CharField(max_length=2000, default = None)
    option2=models.CharField(max_length=2000, default = None)
    option3=models.CharField(max_length=2000, default = None)
    option4=models.CharField(max_length=2000, default = None)
    option1_iscorrect=models.BooleanField(default = 0)
    option2_iscorrect=models.BooleanField(default = 0)
    option3_iscorrect=models.BooleanField(default = 0)
    option4_iscorrect=models.BooleanField(default = 0)
    explanation=models.CharField(max_length=5000, blank=True, default = None)


class question(models.Model):
    xblock_id = models.CharField(max_length=100, blank=False, unique=True, primary_key=True)
    goal = models.CharField(max_length=40, blank=True)
    standard = models.IntegerField(blank=True, default=0)
    subject = models.CharField(max_length=20, blank=True)
    chapter = models.CharField(max_length=50, blank=True)
    topic = models.CharField(max_length=500, blank=True)
    difficulty = models.IntegerField(blank=True, default=1)
    marks = models.IntegerField(blank=True, default=3)
    negativeMarks = models.IntegerField(blank=True, default=-1)
    questionType = models.CharField(max_length=20, blank=True)
    tags=models.CharField(max_length=1000, default = None)
    question=models.CharField(max_length=5000, default = None)
    option1=models.CharField(max_length=2000, default = None)
    option2=models.CharField(max_length=2000, default = None)
    option3=models.CharField(max_length=2000, default = None)
    option4=models.CharField(max_length=2000, default = None)
    option1_iscorrect=models.BooleanField(default = 0)
    option2_iscorrect=models.BooleanField(default = 0)
    option3_iscorrect=models.BooleanField(default = 0)
    option4_iscorrect=models.BooleanField(default = 0)
    explanation=models.CharField(max_length=5000, blank=True, default = None)


class questions(models.Model):
    xblock_id = models.CharField(max_length=100, blank=False, unique=True, primary_key=True)
    goal = models.CharField(max_length=40, blank=True)
    standard = models.IntegerField(blank=True, default=0)
    subject = models.CharField(max_length=20, blank=True)
    chapter = models.CharField(max_length=50, blank=True)
    topic = models.CharField(max_length=100, blank=True)
    difficulty = models.IntegerField(blank=True, default=1)
    marks = models.IntegerField(blank=True, default=3)
    negativeMarks = models.IntegerField(blank=True, default=-1)
    questionType = models.CharField(max_length=20, blank=True)
    tags=models.CharField(max_length=1000, default = None)
    question=models.CharField(max_length=5000, default = None)
    option1=models.CharField(max_length=2000, default = None)
    option2=models.CharField(max_length=2000, default = None)
    option3=models.CharField(max_length=2000, default = None)
    option4=models.CharField(max_length=2000, default = None)
    option1_iscorrect=models.BooleanField(default = 0)
    option2_iscorrect=models.BooleanField(default = 0)
    option3_iscorrect=models.BooleanField(default = 0)
    option4_iscorrect=models.BooleanField(default = 0)
    explanation=models.CharField(max_length=5000, blank=True, default = None)



class exams(models.Model):
    course=models.ForeignKey(exam_info, on_delete=models.CASCADE)
    exam_name=models.CharField(max_length=255)
    image_url=models.CharField(max_length=1000, default = None)

    def __str__(self):
        return str(self.exam_name) + ":"+ str(self.course)


class exams_package(models.Model):
    exam=models.ForeignKey(exams, on_delete=models.CASCADE)
    section=models.CharField(max_length=255)
    image_url=models.CharField(max_length=1000, default = None)
    topic_available=models.BooleanField(default = 1)

    def __str__(self):
        return str(self.exam) + ":"+ str(self.section)



class test_sections(models.Model):
    exams_package=models.ForeignKey(exams_package, on_delete=models.CASCADE)
    section=models.CharField(max_length=100)
    section_name=models.CharField(max_length=100, default = None)

    def __str__(self):
        return str(self.exams_package) + ":"+ str(self.section)


class chapter_updated(models.Model):
    id = models.AutoField(primary_key=True)
    course=models.ForeignKey(exam_info, on_delete=models.CASCADE)
    exam=models.ForeignKey(exams, on_delete=models.CASCADE)
    exams_package=models.ForeignKey(exams_package, on_delete=models.CASCADE)
    chapter=models.CharField(max_length=255)

    class Meta:
            unique_together = (("course","exam","exams_package", "chapter"),)

    def __str__(self):
            return str(self.course) + ":" + str(self.exam) + ":" + str(self.exams_package) + ":" + str(self.chapter)


class live_courses(models.Model):
    teacher=models.ForeignKey(teacher_info, on_delete=models.CASCADE)
    course_id=models.CharField(max_length=60, blank=False)
    course_name=models.CharField(max_length=150, blank=False, default=None)

    def __str__(self):
            return str(self.teacher.firstname)+ " "+ str(self.teacher.firstname) + ":"+ self.course_id

class crashcourse_enrollment(models.Model):
    student=models.ForeignKey(user_info, on_delete=models.CASCADE)
    course=models.ForeignKey(live_courses, on_delete=models.CASCADE)
    is_approved=models.BooleanField(default=0)
    date_joined=models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return u'%s-%s-%s-%s' % (str(self.student.username), str(self.course.course_id), str(self.is_approved), str(self.date_joined))