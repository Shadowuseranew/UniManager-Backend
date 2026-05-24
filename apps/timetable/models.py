from django.conf import settings
from django.db import models
from simple_history.models import HistoricalRecords

from apps.academic.models import Group, Subject


class AttendanceStatus(models.TextChoices):
    PRESENT = 'present', 'Present'
    ABSENT = 'absent', 'Absent'
    LATE = 'late', 'Late'


class Classroom(models.Model):
    name = models.CharField(max_length=50, unique=True)
    capacity = models.PositiveIntegerField()

    class Meta:
        verbose_name = 'Classroom'
        verbose_name_plural = 'Classrooms'

    def __str__(self) -> str:
        return self.name


class TimeSlot(models.Model):
    DAY_CHOICES = [
        (1, 'Monday'),
        (2, 'Tuesday'),
        (3, 'Wednesday'),
        (4, 'Thursday'),
        (5, 'Friday'),
        (6, 'Saturday'),
    ]

    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        ordering = ['day_of_week', 'start_time']
        verbose_name = 'Time Slot'
        verbose_name_plural = 'Time Slots'

    def __str__(self) -> str:
        return f'{self.get_day_of_week_display()} {self.start_time}-{self.end_time}'


class Lesson(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='lessons')
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'teacher'},
    )
    semester = models.ForeignKey(
        'academic.Semester', on_delete=models.CASCADE, related_name='lessons',
    )

    class Meta:
        verbose_name = 'Lesson'
        verbose_name_plural = 'Lessons'
        indexes = [
            models.Index(fields=['time_slot', 'classroom']),
            models.Index(fields=['time_slot', 'teacher']),
        ]

    history = HistoricalRecords()

    def __str__(self) -> str:
        return f'{self.subject.code} - {self.group.name} ({self.time_slot})'


class Attendance(models.Model):
    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE, related_name='attendances',
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='attendances',
        limit_choices_to={'role': 'student'},
    )
    status = models.CharField(
        max_length=10, choices=AttendanceStatus.choices, default=AttendanceStatus.PRESENT,
    )
    date = models.DateField()
    verified_by_face = models.BooleanField(default=False)
    qr_code_hash = models.CharField(max_length=256, null=True, blank=True)
    attempt_time = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        verbose_name = 'Attendance'
        verbose_name_plural = 'Attendances'
        unique_together = ['lesson', 'student']
        indexes = [
            models.Index(fields=['lesson', 'student']),
        ]

    history = HistoricalRecords()

    def __str__(self) -> str:
        return f'{self.student.email} - {self.status} ({self.date})'
