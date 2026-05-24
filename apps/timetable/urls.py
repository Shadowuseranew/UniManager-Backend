from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.timetable.views import (
    AttendanceViewSet,
    ClassroomViewSet,
    LessonViewSet,
    TimeSlotViewSet,
)

router = DefaultRouter()
router.register(r'classrooms', ClassroomViewSet)
router.register(r'time-slots', TimeSlotViewSet)
router.register(r'lessons', LessonViewSet)
router.register(r'attendances', AttendanceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
