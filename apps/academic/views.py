from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import viewsets

from core.settings import CACHE_TTL

from apps.academic.models import (
    AcademicYear,
    Department,
    Enrollment,
    Faculty,
    Group,
    Semester,
    Subject,
)
from apps.academic.serializers import (
    AcademicYearSerializer,
    DepartmentSerializer,
    EnrollmentSerializer,
    FacultySerializer,
    GroupSerializer,
    SemesterSerializer,
    SubjectSerializer,
)


class FacultyViewSet(viewsets.ModelViewSet):
    """CRUD for faculties. List is cached (5 min). Returns nested departments."""

    queryset = Faculty.objects.prefetch_related('departments').all()
    serializer_class = FacultySerializer

    @method_decorator(cache_page(CACHE_TTL))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class DepartmentViewSet(viewsets.ModelViewSet):
    """CRUD for departments."""

    queryset = Department.objects.select_related('faculty').all()
    serializer_class = DepartmentSerializer


class SubjectViewSet(viewsets.ModelViewSet):
    """CRUD for subjects."""

    queryset = Subject.objects.select_related('department').all()
    serializer_class = SubjectSerializer


class AcademicYearViewSet(viewsets.ModelViewSet):
    """CRUD for academic years."""

    queryset = AcademicYear.objects.all()
    serializer_class = AcademicYearSerializer


class SemesterViewSet(viewsets.ModelViewSet):
    """CRUD for semesters. Nested academic year."""

    queryset = Semester.objects.select_related('academic_year').all()
    serializer_class = SemesterSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """CRUD for groups. List is cached (5 min)."""

    queryset = Group.objects.select_related('department', 'semester').all()
    serializer_class = GroupSerializer

    @method_decorator(cache_page(CACHE_TTL))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class EnrollmentViewSet(viewsets.ModelViewSet):
    """CRUD for student enrollments in groups."""

    queryset = Enrollment.objects.select_related('student', 'group', 'semester').all()
    serializer_class = EnrollmentSerializer
