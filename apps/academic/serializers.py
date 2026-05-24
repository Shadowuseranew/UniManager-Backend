from rest_framework import serializers

from apps.academic.models import (
    AcademicYear,
    Department,
    Enrollment,
    Faculty,
    Group,
    Semester,
    Subject,
)


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name']


class FacultySerializer(serializers.ModelSerializer):
    departments = DepartmentSerializer(many=True, read_only=True)

    class Meta:
        model = Faculty
        fields = ['id', 'name', 'slug', 'departments']


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'code', 'name', 'department']


class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = ['id', 'name', 'is_active']


class SemesterSerializer(serializers.ModelSerializer):
    academic_year = AcademicYearSerializer(read_only=True)

    class Meta:
        model = Semester
        fields = ['id', 'number', 'start_date', 'end_date', 'academic_year']


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name', 'department', 'semester', 'year_of_study']


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'group', 'semester', 'enrolled_at']
        read_only_fields = ['enrolled_at']
