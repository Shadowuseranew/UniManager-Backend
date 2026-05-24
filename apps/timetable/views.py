from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from core.settings import CACHE_TTL

from apps.timetable.models import Attendance, Classroom, Lesson, TimeSlot
from apps.timetable.serializers import (
    AttendanceBulkSerializer,
    AttendanceSerializer,
    ClassroomSerializer,
    LessonDetailSerializer,
    LessonSerializer,
    QRVerifySerializer,
    TimeSlotSerializer,
)
from apps.timetable.services import (
    CollisionError,
    bulk_mark_attendance,
    create_lesson,
    verify_qr_token,
)


class ClassroomViewSet(viewsets.ModelViewSet):
    """CRUD for classrooms."""

    queryset = Classroom.objects.all()
    serializer_class = ClassroomSerializer


class TimeSlotViewSet(viewsets.ModelViewSet):
    """CRUD for time slots (day + time range)."""

    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer


class LessonViewSet(viewsets.ModelViewSet):
    """CRUD for lessons with collision detection.

    Custom endpoints:
        GET /by-group/{id}/   — timetable for a group (cached 5 min)
        GET /by-teacher/{id}/ — timetable for a teacher (cached 5 min)
    """

    queryset = Lesson.objects.select_related(
        'subject', 'group', 'classroom', 'time_slot', 'teacher',
    ).all()

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return LessonDetailSerializer
        return LessonSerializer

    def perform_create(self, serializer):
        try:
            validated = serializer.validated_data
            create_lesson(
                subject_id=validated['subject'].id,
                group_id=validated['group'].id,
                classroom_id=validated['classroom'].id,
                time_slot_id=validated['time_slot'].id,
                teacher_id=validated['teacher'].id,
                semester_id=validated['semester'].id,
            )
        except CollisionError as e:
            return Response({'error': str(e)}, status=status.HTTP_409_CONFLICT)

    @method_decorator(cache_page(CACHE_TTL))
    @action(detail=False, methods=['get'], url_path=r'by-group/(?P<group_id>\d+)')
    def by_group(self, request: Request, group_id: int | None = None) -> Response:
        lessons = self.get_queryset().filter(group_id=group_id)
        serializer = LessonDetailSerializer(lessons, many=True)
        return Response(serializer.data)

    @method_decorator(cache_page(CACHE_TTL))
    @action(detail=False, methods=['get'], url_path=r'by-teacher/(?P<teacher_id>\d+)')
    def by_teacher(self, request: Request, teacher_id: int | None = None) -> Response:
        lessons = self.get_queryset().filter(teacher_id=teacher_id)
        serializer = LessonDetailSerializer(lessons, many=True)
        return Response(serializer.data)


class AttendanceViewSet(viewsets.ModelViewSet):
    """CRUD for attendance records.

    Custom endpoints:
        POST /bulk/               — mark attendance for multiple students
        GET  /by-lesson/{id}/     — attendance for a specific lesson
        GET  /by-student/{id}/    — attendance history for a student
    """

    queryset = Attendance.objects.select_related('lesson', 'student').all()
    serializer_class = AttendanceSerializer

    @action(detail=False, methods=['post'], url_path='bulk')
    def bulk(self, request: Request) -> Response:
        serializer = AttendanceBulkSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            attendances = bulk_mark_attendance(
                lesson_id=serializer.validated_data['lesson_id'],
                records=serializer.validated_data['records'],
            )
            result = AttendanceSerializer(attendances, many=True)
            return Response(result.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path=r'by-lesson/(?P<lesson_id>\d+)')
    def by_lesson(self, request: Request, lesson_id: int | None = None) -> Response:
        attendances = self.get_queryset().filter(lesson_id=lesson_id)
        serializer = self.get_serializer(attendances, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path=r'by-student/(?P<student_id>\d+)')
    def by_student(self, request: Request, student_id: int | None = None) -> Response:
        attendances = self.get_queryset().filter(student_id=student_id)
        serializer = self.get_serializer(attendances, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='verify-qr')
    def verify_qr(self, request: Request) -> Response:
        serializer = QRVerifySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        if verify_qr_token(data['secret'], data['token']):
            mark_attendance(
                lesson_id=data['lesson_id'],
                student_id=data['student_id'],
                status='present',
            )
            return Response({'verified': True, 'message': 'Attendance marked.'})
        return Response(
            {'verified': False, 'error': 'Invalid or expired QR token.'},
            status=status.HTTP_401_UNAUTHORIZED,
        )
