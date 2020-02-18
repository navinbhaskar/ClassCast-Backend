from .models import teacher_student_interaction, teacher_info
from rest_framework import serializers

class teachers_serializer(serializers.ModelSerializer):
    class Meta:
        model = teacher_info
        fields = '__all__'

class teacher_student_interaction_serializer(serializers.ModelSerializer):
    
    class Meta:
        model = teacher_student_interaction
        fields = '__all__'

class teacher_student_interaction_serializer1(serializers.ModelSerializer):
    
    class Meta:
        model = teacher_student_interaction
        fields = ('teacher',)
