from datetime import date, time, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.academic.models import (
    AcademicYear,
    Department,
    Enrollment,
    Faculty,
    Group,
    Semester,
    Subject,
)
from apps.timetable.models import Classroom, Lesson, TimeSlot
from apps.users.models import UserRole

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate database with realistic demo data for diploma defense.'

    def handle(self, *args, **options):
        self._clean()
        self._create_users()
        self._create_academic_year()
        self._create_faculties()
        self._create_classrooms()
        self._create_time_slots()
        self._create_lessons()
        self._create_enrollments()
        self._create_attendances()
        self.stdout.write(self.style.SUCCESS(''))
        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))
        self.stdout.write(self.style.SUCCESS('  Superadmin: superadmin@uni.com / admin123'))
        self.stdout.write(self.style.SUCCESS('  Admin:      admin@uni.com      / admin123'))
        self.stdout.write(self.style.SUCCESS('  Students:   student123'))
        self.stdout.write(self.style.SUCCESS('  Teachers:   teacher123'))

    def _clean(self) -> None:
        self.stdout.write('Cleaning existing data...')
        try:
            from apps.timetable.models import Attendance
            Attendance.objects.all().delete()
        except ImportError:
            pass
        Lesson.objects.all().delete()
        TimeSlot.objects.all().delete()
        Classroom.objects.all().delete()
        Enrollment.objects.all().delete()
        Group.objects.all().delete()
        Subject.objects.all().delete()
        Department.objects.all().delete()
        Faculty.objects.all().delete()
        Semester.objects.all().delete()
        AcademicYear.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

    def _create_users(self) -> None:
        self.stdout.write('Creating users...')

        User.objects.create_superuser(
            email='superadmin@uni.com', username='superadmin',
            password='admin123', role=UserRole.SUPERADMIN,
        )
        User.objects.create_user(
            email='admin@uni.com', username='admin',
            password='admin123', role=UserRole.ADMIN,
        )

        teachers = [
            ('prof.ahmedov@uni.com', 'ahmedov_a', 'Prof. A.', 'Ahmedov'),
            ('dr.berdiyev@uni.com', 'berdiyev_b', 'Dr. B.', 'Berdiyev'),
            ('dr.raximova@uni.com', 'raximova_d', 'Dr. D.', 'Raximova'),
        ]
        for email, username, first, last in teachers:
            User.objects.create_user(
                email=email, username=username, password='teacher123',
                role=UserRole.TEACHER, first_name=first, last_name=last,
            )

        students = [
            ('aliyev@student.com', 'aliyev_v', 'Vali', 'Aliyev'),
            ('karimova@student.com', 'karimova_g', 'Gul', 'Karimova'),
            ('toirov@student.com', 'toirov_s', 'Sardor', 'Toirov'),
            ('usmanova@student.com', 'usmanova_l', 'Lola', 'Usmanova'),
            ('hasanov@student.com', 'hasanov_b', 'Bekzod', 'Hasanov'),
            ('norboyeva@student.com', 'norboyeva_n', 'Nigora', 'Norboyeva'),
            ('xolmatov@student.com', 'xolmatov_j', 'Javohir', 'Xolmatov'),
            ('asqarova@student.com', 'asqarova_m', 'Madina', 'Asqarova'),
            ('sharipov@student.com', 'sharipov_e', 'Eldor', 'Sharipov'),
            ('sattorova@student.com', 'sattorova_z', 'Zilola', 'Sattorova'),
            ('ibragimov@student.com', 'ibragimov_o', 'Otabek', 'Ibragimov'),
            ('murodova@student.com', 'murodova_f', 'Feruza', 'Murodova'),
            ('qodirov@student.com', 'qodirov_a', 'Akmal', 'Qodirov'),
            ('jorayeva@student.com', 'jorayeva_d', 'Dildora', "Jo'rayeva"),
            ('rahimov@student.com', 'rahimov_m', 'Murod', 'Rahimov'),
        ]
        for email, username, first, last in students:
            User.objects.create_user(
                email=email, username=username, password='student123',
                role=UserRole.STUDENT, first_name=first, last_name=last,
            )

        self.stdout.write('  15 students, 3 teachers, 2 admins')

    def _create_academic_year(self) -> None:
        year, _ = AcademicYear.objects.get_or_create(
            name='2025-2026', defaults={'is_active': True},
        )
        Semester.objects.get_or_create(
            academic_year=year, number=1,
            defaults={'start_date': date(2025, 9, 1), 'end_date': date(2026, 1, 25)},
        )

    def _create_faculties(self) -> None:
        self.stdout.write('Creating faculties & departments...')

        cei = Faculty.objects.create(name='Kompyuter Injiniringi', slug='ce')
        ai_robot = Faculty.objects.create(name="Sun'iy Intellekt va Robototexnika", slug='ai')

        dep_se = Department.objects.create(name='Dasturiy injiniring', faculty=cei)
        dep_is = Department.objects.create(name='Axborot xavfsizligi', faculty=cei)
        dep_ai = Department.objects.create(name="Sun'iy intellekt", faculty=ai_robot)

        semester = Semester.objects.first()

        Group.objects.create(
            name='SE-2026-1', department=dep_se, semester=semester, year_of_study=2,
        )
        Group.objects.create(
            name='DS-2026-1', department=dep_is, semester=semester, year_of_study=2,
        )
        Group.objects.create(
            name='AI-2025-1', department=dep_ai, semester=semester, year_of_study=3,
        )

        subjects_data = [
            ("Algoritmlar va ma'lumotlar tuzilmasi", 'CE201', dep_se),
            ('Django Web Framework', 'CE301', dep_se),
            ("Ma'lumotlar bazasi tizimlari", 'CE202', dep_is),
            ("Sun'iy intellekt asoslari", 'AI201', dep_ai),
            ('Robototexnika', 'AI301', dep_ai),
        ]
        for name, code, dept in subjects_data:
            Subject.objects.create(name=name, code=code, department=dept)

        self.stdout.write('  2 faculties, 3 departments, 5 subjects, 3 groups')

    def _create_classrooms(self) -> None:
        self.stdout.write('Creating classrooms...')
        for name, cap in [
            ('201-Auditoriya', 40), ('305-Lab', 25), ('101-Media', 60),
        ]:
            Classroom.objects.create(name=name, capacity=cap)

    def _create_time_slots(self) -> None:
        self.stdout.write('Creating time slots...')
        pairs = [
            (time(9, 0), time(10, 30)),
            (time(10, 45), time(12, 15)),
            (time(13, 0), time(14, 30)),
        ]
        for day in (1, 2, 3, 4):
            for start, end in pairs:
                TimeSlot.objects.create(
                    day_of_week=day, start_time=start, end_time=end,
                )

    def _create_lessons(self) -> None:
        self.stdout.write('Creating lessons...')
        semester = Semester.objects.first()
        subjects = {s.code: s for s in Subject.objects.all()}
        timeslots = list(TimeSlot.objects.all())
        classrooms = list(Classroom.objects.all())
        groups = {g.name: g for g in Group.objects.all()}
        teachers = {u.first_name: u for u in User.objects.filter(role=UserRole.TEACHER)}

        plan = [
            (groups['SE-2026-1'], subjects['CE201'], teachers['Prof. A.'], timeslots[0], classrooms[0]),
            (groups['SE-2026-1'], subjects['CE301'], teachers['Prof. A.'], timeslots[1], classrooms[0]),
            (groups['SE-2026-1'], subjects['CE201'], teachers['Prof. A.'], timeslots[3], classrooms[0]),
            (groups['SE-2026-1'], subjects['CE301'], teachers['Dr. D.'], timeslots[4], classrooms[2]),
            (groups['DS-2026-1'], subjects['CE202'], teachers['Dr. B.'], timeslots[2], classrooms[1]),
            (groups['DS-2026-1'], subjects['CE202'], teachers['Dr. B.'], timeslots[6], classrooms[1]),
            (groups['DS-2026-1'], subjects['CE201'], teachers['Prof. A.'], timeslots[7], classrooms[0]),
            (groups['AI-2025-1'], subjects['AI201'], teachers['Dr. D.'], timeslots[5], classrooms[2]),
            (groups['AI-2025-1'], subjects['AI301'], teachers['Dr. B.'], timeslots[9], classrooms[1]),
            (groups['AI-2025-1'], subjects['AI201'], teachers['Dr. D.'], timeslots[10], classrooms[2]),
        ]
        for group, subject, teacher, ts, cr in plan:
            Lesson.objects.create(
                subject=subject, group=group, teacher=teacher,
                classroom=cr, time_slot=ts, semester=semester,
            )
        self.stdout.write('  10 lessons created')

    def _create_enrollments(self) -> None:
        self.stdout.write('Creating enrollments...')
        semester = Semester.objects.first()
        groups = list(Group.objects.all())
        students = list(User.objects.filter(role=UserRole.STUDENT))

        for i, student in enumerate(students):
            group = groups[i // 5]
            Enrollment.objects.create(
                student=student, group=group, semester=semester,
            )

    def _create_attendances(self) -> None:
        self.stdout.write('Creating attendance records...')
        try:
            from apps.timetable.models import Attendance
        except ImportError:
            return

        lessons = list(Lesson.objects.all())
        students = list(User.objects.filter(role=UserRole.STUDENT))
        status_pool = ['present', 'present', 'present', 'present', 'late', 'absent']

        for lesson in lessons:
            for student in students:
                status = status_pool[(lesson.id + student.id) % len(status_pool)]
                lesson_date = date.today() - timedelta(days=lesson.id % 5)
                Attendance.objects.create(
                    lesson=lesson, student=student,
                    status=status, date=lesson_date,
                )
