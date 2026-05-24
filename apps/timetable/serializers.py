from rest_framework import serializers

from apps.academic.models import Group, Subject
from apps.academic.serializers import GroupSerializer, SubjectSerializer
from apps.timetable.models import Attendance, Classroom, Lesson, TimeSlot
from apps.users.models import User


class ClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = ['id', 'name', 'capacity']


class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = ['id', 'day_of_week', 'start_time', 'end_time']


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = [
            'id', 'subject', 'group', 'classroom', 'time_slot', 'teacher', 'semester',
        ]


class LessonDetailSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)
    group = GroupSerializer(read_only=True)
    classroom = ClassroomSerializer(read_only=True)
    time_slot = TimeSlotSerializer(read_only=True)

    class Meta:
        model = Lesson
        fields = [
            'id', 'subject', 'group', 'classroom', 'time_slot', 'teacher', 'semester',
        ]


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['id', 'lesson', 'student', 'status', 'date']


class AttendanceBulkSerializer(serializers.Serializer):
    lesson_id = serializers.IntegerField()
    records = serializers.ListField(child=serializers.DictField())


class QRVerifySerializer(serializers.Serializer):
    lesson_id = serializers.IntegerField()
    student_id = serializers.IntegerField()
    token = serializers.CharField(max_length=10)
    secret = serializers.CharField(max_length=256)
