from django.db import models

class user_info(models.Model):
    gender_choices = [('1', 'Male'), ('2', 'Female')]
    standard_choices = [('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5','5'),('6', '6'),('7', '7'), ('8', '8'), ('9', '9'), ('10', '10'), ('11','11'),('12', '12'),('13','13'),('14','SSC'),('15','Bank PO'),('16','Railways'),('17','Bank Clerk'),('18','IIT JAM'),('19','NET JRF'),('20','TIFR'),('21','KVS TGT/PGT'),('22','NVSNVS TGT/PGT'),('23','DSSSB TGT/PGT'),('24','APSAPS TGT/PGT'),('25','UGC NET'),('26','GATE'),('27','UPPRPB'),('28','UP LT'),('29','')]

    student_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100, blank=False, unique=True)
    firstname = models.CharField(max_length=40, blank=False)
    lastname = models.CharField(max_length=40, blank=False)
    gender = models.CharField(max_length=9, choices=gender_choices, default='1')
    phone_number = models.CharField(max_length=13, blank =False, unique=True)
    standard = models.CharField(max_length=5, choices=standard_choices, default='18')
    stream = models.CharField(max_length=20, blank=True)
    area = models.CharField(max_length=40, blank=True)
    pincode =  models.CharField(max_length=10, blank=True)
    karma_point = models.CharField(max_length=40, blank =True)
    email = models.CharField(max_length=60, blank=True, unique=True, null=True,)
    photo =  models.CharField(max_length=300, blank=True)
    goal = models.CharField(max_length=10, blank =True)
    school = models.CharField(max_length=100, blank =True)
    coachings = models.CharField(max_length=500, blank =True)
    date_joined = models.DateTimeField(null=True, blank=True)
    dob = models.DateTimeField(null=True, blank=True)
    language = models.CharField(max_length=40, blank=True)
    class Meta:
        db_table = 'classcast_user_info'

    def __str__(self):
        return u'%s-%s' % (str(self.username), str(self.standard))


class exam_info(models.Model):
    exam_id = models.CharField(max_length=10, primary_key=True)
    exam_name = models.CharField(max_length=40)
    subjects = models.CharField(max_length=500, blank =True)
    exam_type = models.CharField(max_length=100, blank =True)

    def __str__(self):
        return u'%s-%s' % (str(self.exam_id), str(self.exam_name))


class parents_details(models.Model):
    relationship_choices = [('1', 'Father'), ('2', 'Mother'), ('3', 'Brother'), ('4', 'Sister'), ('5', 'Other')]

    student = models.ForeignKey(user_info, on_delete=models.CASCADE)
    name=models.CharField(max_length=50, blank=False)
    relationship_to_student=models.CharField(max_length=15, choices=relationship_choices, default='5')
    contact_number=models.CharField(max_length=15, blank=False)

    def __str__(self):
        return u'%s %s' % (str(self.student), str(self.relationship_to_student))