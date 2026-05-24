from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.academic.views import (
    AcademicYearViewSet,
    DepartmentViewSet,
    EnrollmentViewSet,
    FacultyViewSet,
    GroupViewSet,
    SemesterViewSet,
    SubjectViewSet,
)

router = DefaultRouter()
router.register(r'faculties', FacultyViewSet)
router.register(r'departments', DepartmentViewSet)
router.register(r'subjects', SubjectViewSet)
router.register(r'academic-years', AcademicYearViewSet)
router.register(r'semesters', SemesterViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'enrollments', EnrollmentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
