from datetime import date, timedelta

from django.db.models import Count
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.academic.models import Department, Faculty, Group, Subject
from apps.timetable.models import Attendance, AttendanceStatus, Lesson
from apps.users.models import User, UserRole


class DashboardStatsView(APIView):
    """Return overall system statistics for the admin dashboard."""

    def get(self, request):
        today = date.today()

        faculties_count = Faculty.objects.count()
        departments_count = Department.objects.count()
        subjects_count = Subject.objects.count()
        groups_count = Group.objects.count()

        students_count = User.objects.filter(role=UserRole.STUDENT).count()
        teachers_count = User.objects.filter(role=UserRole.TEACHER).count()
        admins_count = User.objects.filter(
            role__in=[UserRole.ADMIN, UserRole.SUPERADMIN],
        ).count()

        lessons_count = Lesson.objects.count()
        lessons_today = Lesson.objects.filter(semester__groups__isnull=False).count()

        today_attendances = Attendance.objects.filter(date=today)
        total_today = today_attendances.count()
        present_today = today_attendances.filter(status=AttendanceStatus.PRESENT).count()
        late_today = today_attendances.filter(status=AttendanceStatus.LATE).count()
        absent_today = today_attendances.filter(status=AttendanceStatus.ABSENT).count()
        attendance_percent = (
            round((present_today / total_today * 100), 1) if total_today else 0
        )

        last_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]
        attendance_trend = []
        for day in last_7_days:
            day_att = Attendance.objects.filter(date=day)
            total = day_att.count()
            present = day_att.filter(status=AttendanceStatus.PRESENT).count()
            attendance_trend.append({
                'date': day.isoformat(),
                'total': total,
                'present': present,
                'percent': round((present / total * 100), 1) if total else 0,
            })

        enrollment_stats = []
        for group in Group.objects.all():
            count = group.enrollments.count()
            enrollment_stats.append({
                'group': group.name,
                'students_enrolled': count,
            })

        role_distribution = {
            'students': students_count,
            'teachers': teachers_count,
            'admins': admins_count,
        }

        overall_attendance = Attendance.objects.all()
        overall_total = overall_attendance.count()
        overall_present = overall_attendance.filter(status=AttendanceStatus.PRESENT).count()
        overall_percent = (
            round((overall_present / overall_total * 100), 1) if overall_total else 0
        )

        return Response({
            'summary': {
                'faculties': faculties_count,
                'departments': departments_count,
                'subjects': subjects_count,
                'groups': groups_count,
                'lessons_total': lessons_count,
                'lessons_today': lessons_today,
            },
            'users': {
                'total': students_count + teachers_count + admins_count,
                'role_distribution': role_distribution,
            },
            'attendance': {
                'overall': {
                    'total_records': overall_total,
                    'present': overall_present,
                    'attendance_rate_percent': overall_percent,
                },
                'today': {
                    'date': today.isoformat(),
                    'total': total_today,
                    'present': present_today,
                    'late': late_today,
                    'absent': absent_today,
                    'attendance_rate_percent': attendance_percent,
                },
                'trend_last_7_days': attendance_trend,
            },
            'enrollments': {
                'total': sum(e['students_enrolled'] for e in enrollment_stats),
                'by_group': enrollment_stats,
            },
            'system': {
                'audit_trail_enabled': True,
                'collision_detection': True,
                'cache_enabled': True,
                'qr_totp_interval_seconds': 3,
            },
        })
