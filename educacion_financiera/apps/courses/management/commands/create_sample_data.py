from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random

from educacion_financiera.apps.courses.models import (
    Category, Course, Module, Lesson, Enrollment, LessonProgress, Certificate
)
from educacion_financiera.apps.profiles.models import Profile, Badge, UserBadge

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample data for the e-learning platform'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete existing data before creating new sample data',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write('Deleting existing data...')
            Category.objects.all().delete()
            Badge.objects.all().delete()
            # Users and profiles will cascade

        self.create_categories()
        self.create_badges()
        self.create_sample_users()
        self.create_courses()
        self.create_sample_progress()

        self.stdout.write(
            self.style.SUCCESS('Successfully created sample data!')
        )

    def create_categories(self):
        """Create course categories"""
        self.stdout.write('Creating categories...')

        categories_data = [
            {
                'name': 'Finanzas Personales',
                'slug': 'finanzas-personales',
                'description': 'Aprende a manejar tu dinero personal y familiar'
            },
            {
                'name': 'Inversiones',
                'slug': 'inversiones',
                'description': 'Descubre el mundo de las inversiones y multiplica tu dinero'
            },
            {
                'name': 'Emprendimiento',
                'slug': 'emprendimiento',
                'description': 'Desarrolla habilidades para crear y gestionar tu propio negocio'
            },
            {
                'name': 'Criptomonedas',
                'slug': 'criptomonedas',
                'description': 'Entiende el mundo de las criptomonedas y blockchain'
            },
            {
                'name': 'Planificación Financiera',
                'slug': 'planificacion-financiera',
                'description': 'Planifica tu futuro financiero y alcanza tus metas'
            }
        ]

        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'  Created category: {category.name}')

    def create_badges(self):
        """Create achievement badges"""
        self.stdout.write('Creating badges...')

        badges_data = [
            {
                'name': 'Primer Paso',
                'description': 'Completa tu primera lección',
                'icon': 'fas fa-star',
                'badge_type': 'completion',
                'color': 'success',
                'required_value': 1
            },
            {
                'name': 'Estudiante Dedicado',
                'description': 'Completa 5 lecciones',
                'icon': 'fas fa-book',
                'badge_type': 'completion',
                'color': 'primary',
                'required_value': 5
            },
            {
                'name': 'Aprendiz Experto',
                'description': 'Completa 25 lecciones',
                'icon': 'fas fa-graduation-cap',
                'badge_type': 'completion',
                'color': 'warning',
                'required_value': 25
            },
            {
                'name': 'Racha de Fuego',
                'description': 'Mantén una racha de 7 días',
                'icon': 'fas fa-fire',
                'badge_type': 'streak',
                'color': 'danger',
                'required_value': 7
            },
            {
                'name': 'Estudiante Constante',
                'description': 'Mantén una racha de 30 días',
                'icon': 'fas fa-calendar-check',
                'badge_type': 'streak',
                'color': 'info',
                'required_value': 30
            },
            {
                'name': 'Maratonista del Aprendizaje',
                'description': 'Estudia por 10 horas',
                'icon': 'fas fa-clock',
                'badge_type': 'time',
                'color': 'secondary',
                'required_value': 600  # 10 hours in minutes
            }
        ]

        for badge_data in badges_data:
            badge, created = Badge.objects.get_or_create(
                name=badge_data['name'],
                defaults=badge_data
            )
            if created:
                self.stdout.write(f'  Created badge: {badge.name}')

    def create_sample_users(self):
        """Create sample users with different roles"""
        self.stdout.write('Creating sample users...')

        # Create instructor
        instructor, created = User.objects.get_or_create(
            email='instructor@example.com',
            defaults={
                'name': 'María González',
                'is_teacher': True,
                'is_student': False
            }
        )
        if created:
            instructor.set_password('demo123')
            instructor.save()
            self.stdout.write('  Created instructor: instructor@example.com')

        # Create instructor profile
        instructor_profile, created = Profile.objects.get_or_create(
            user=instructor,
            defaults={
                'role': 'instructor',
                'bio': 'Experta en finanzas con más de 15 años de experiencia.',
                'title': 'Consultora Financiera',
                'company': 'FinanceExpert Consulting',
                'experience_years': 15,
                'experience_level': 'advanced',
                'interests': 'Inversiones, Planificación financiera, Educación'
            }
        )

        # Create sample students
        students_data = [
            {
                'email': 'student1@example.com',
                'name': 'Carlos Rodríguez',
                'profile_data': {
                    'role': 'student',
                    'experience_level': 'beginner',
                    'interests': 'Ahorro, Inversiones básicas',
                    'total_study_time': 180,  # 3 hours
                    'current_streak': 5,
                    'longest_streak': 12,
                    'courses_completed': 1
                }
            },
            {
                'email': 'student2@example.com',
                'name': 'Ana López',
                'profile_data': {
                    'role': 'student',
                    'experience_level': 'intermediate',
                    'interests': 'Inversiones, Emprendimiento',
                    'total_study_time': 420,  # 7 hours
                    'current_streak': 12,
                    'longest_streak': 25,
                    'courses_completed': 2
                }
            }
        ]

        for student_data in students_data:
            student, created = User.objects.get_or_create(
                email=student_data['email'],
                defaults={
                    'name': student_data['name'],
                    'is_student': True,
                    'is_teacher': False
                }
            )
            if created:
                student.set_password('demo123')
                student.save()
                self.stdout.write(f'  Created student: {student.email}')

                # Create profile
                Profile.objects.get_or_create(
                    user=student,
                    defaults=student_data['profile_data']
                )

    def create_courses(self):
        """Create sample courses with modules and lessons"""
        self.stdout.write('Creating courses...')

        instructor = User.objects.get(email='instructor@example.com')

        courses_data = [
            {
                'title': 'Introducción a las Finanzas Personales',
                'slug': 'introduccion-finanzas-personales',
                'category': 'finanzas-personales',
                'overview': 'Aprende los conceptos básicos para manejar tu dinero de manera inteligente.',
                'price': 0,
                'modules': [
                    {
                        'title': 'Fundamentos del Dinero',
                        'description': 'Conceptos básicos sobre el dinero y su importancia',
                        'lessons': [
                            {
                                'title': '¿Qué es el dinero?',
                                'description': 'Introducción al concepto de dinero y su función en la sociedad.',
                                'video_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
                            },
                            {
                                'title': 'Historia del dinero',
                                'description': 'Evolución del dinero desde el trueque hasta las monedas digitales.',
                                'video_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
                            },
                            {
                                'title': 'Tipos de dinero',
                                'description': 'Efectivo, dinero electrónico y nuevas formas de pago.',
                                'video_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
                            }
                        ]
                    },
                    {
                        'title': 'Presupuesto Personal',
                        'description': 'Aprende a crear y mantener un presupuesto personal',
                        'lessons': [
                            {
                                'title': 'Cómo hacer un presupuesto',
                                'description': 'Pasos para crear tu primer presupuesto personal.',
                                'video_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
                            },
                            {
                                'title': 'Herramientas para presupuestar',
                                'description': 'Apps y herramientas digitales para gestionar tu presupuesto.',
                                'video_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
                            }
                        ]
                    }
                ]
            },
            {
                'title': 'Inversiones para Principiantes',
                'slug': 'inversiones-principiantes',
                'category': 'inversiones',
                'overview': 'Descubre cómo empezar a invertir tu dinero de forma segura y rentable.',
                'price': 99,
                'modules': [
                    {
                        'title': 'Conceptos Básicos de Inversión',
                        'description': 'Fundamentos que todo inversionista debe conocer',
                        'lessons': [
                            {
                                'title': '¿Qué es invertir?',
                                'description': 'Diferencia entre ahorrar e invertir.',
                                'video_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
                            },
                            {
                                'title': 'Riesgo vs Rentabilidad',
                                'description': 'Comprende la relación entre riesgo y retorno.',
                                'video_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
                            }
                        ]
                    }
                ]
            },
            {
                'title': 'Criptomonedas: Guía Completa',
                'slug': 'criptomonedas-guia-completa',
                'category': 'criptomonedas',
                'overview': 'Todo lo que necesitas saber sobre Bitcoin, Ethereum y otras criptomonedas.',
                'price': 149,
                'modules': [
                    {
                        'title': 'Introducción a las Criptomonedas',
                        'description': 'Conceptos básicos del mundo cripto',
                        'lessons': [
                            {
                                'title': '¿Qué es Bitcoin?',
                                'description': 'Historia y funcionamiento de la primera criptomoneda.',
                                'video_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
                            },
                            {
                                'title': 'Blockchain explicado',
                                'description': 'Tecnología detrás de las criptomonedas.',
                                'video_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
                            }
                        ]
                    }
                ]
            }
        ]

        for course_data in courses_data:
            category = Category.objects.get(slug=course_data['category'])

            course, created = Course.objects.get_or_create(
                slug=course_data['slug'],
                defaults={
                    'title': course_data['title'],
                    'category': category,
                    'instructor': instructor,
                    'overview': course_data['overview'],
                    'price': course_data['price'],
                    'visibility': 'public'
                }
            )

            if created:
                self.stdout.write(f'  Created course: {course.title}')

                # Create modules and lessons
                for module_order, module_data in enumerate(course_data['modules'], 1):
                    module = Module.objects.create(
                        course=course,
                        title=module_data['title'],
                        description=module_data['description'],
                        order=module_order
                    )

                    for lesson_order, lesson_data in enumerate(module_data['lessons'], 1):
                        Lesson.objects.create(
                            module=module,
                            title=lesson_data['title'],
                            description=lesson_data['description'],
                            video_url=lesson_data['video_url'],
                            order=lesson_order
                        )

    def create_sample_progress(self):
        """Create sample enrollments and progress"""
        self.stdout.write('Creating sample progress...')

        students = User.objects.filter(is_student=True)
        courses = Course.objects.all()

        for student in students:
            # Enroll student in some courses
            courses_to_enroll = random.sample(list(courses), min(2, len(courses)))

            for course in courses_to_enroll:
                enrollment, created = Enrollment.objects.get_or_create(
                    student=student,
                    course=course,
                    defaults={'active': True}
                )

                if created:
                    self.stdout.write(f'  Enrolled {student.email} in {course.title}')

                    # Create some lesson progress
                    lessons = Lesson.objects.filter(module__course=course)
                    lessons_to_complete = random.sample(
                        list(lessons),
                        random.randint(1, min(3, len(lessons)))
                    )

                    for lesson in lessons_to_complete:
                        progress = LessonProgress.objects.create(
                            student=student,
                            lesson=lesson,
                            is_completed=True,
                            completed_at=timezone.now() - timedelta(days=random.randint(1, 30)),
                            time_spent=random.randint(300, 1800)  # 5-30 minutes
                        )

                    # Award some badges
                    self.award_badges(student)

    def award_badges(self, user):
        """Award badges to user based on their activity"""
        badges = Badge.objects.filter(is_active=True)

        # Simple badge awarding logic
        completed_lessons = LessonProgress.objects.filter(
            student=user,
            is_completed=True
        ).count()

        for badge in badges:
            if badge.badge_type == 'completion' and completed_lessons >= badge.required_value:
                UserBadge.objects.get_or_create(
                    user=user,
                    badge=badge
                )
            elif badge.badge_type == 'streak' and user.profile.current_streak >= badge.required_value:
                UserBadge.objects.get_or_create(
                    user=user,
                    badge=badge
                )
            elif badge.badge_type == 'time' and user.profile.total_study_time >= badge.required_value:
                UserBadge.objects.get_or_create(
                    user=user,
                    badge=badge
                )
