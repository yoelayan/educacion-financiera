from django.conf import settings
from django.db import models
from django.db.models import Count
from educacion_financiera.apps.courses.models import Category, Course, Enrollment, Certificate
from educacion_financiera.apps.profiles.models import Profile


def global_context(request):
    """
    Context processor que proporciona datos globales para toda la aplicación
    """
    context = {
        'site_name': 'Educación Financiera',
        'categories': Category.objects.annotate(
            course_count=Count('courses', filter=models.Q(courses__visibility='public'))
        ),
        'user_stats': {},
        'navigation_items': [],
    }

    # Datos específicos para usuarios autenticados
    if request.user.is_authenticated:
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            profile = Profile.objects.create(user=request.user)

        # Estadísticas del usuario
        enrollments = Enrollment.objects.filter(student=request.user, active=True)
        context['user_stats'] = {
            'enrolled_courses': enrollments.count(),
            'certificates': Certificate.objects.filter(student=request.user, is_active=True).count(),
            'total_study_time': profile.total_study_time,
            'current_streak': profile.current_streak,
            'profile': profile,
        }

        # Items de navegación personalizados según el rol
        if request.user.is_teacher:
            context['navigation_items'] = [
                {
                    'name': 'Dashboard',
                    'url': '/dashboard/',
                    'icon': 'fas fa-tachometer-alt',
                    'active': request.resolver_match.url_name == 'home'
                },
                {
                    'name': 'Mis Cursos',
                    'url': '/admin/courses/course/',
                    'icon': 'fas fa-chalkboard-teacher',
                    'dropdown': True,
                    'items': [
                        {'name': 'Crear Curso', 'url': '/admin/courses/course/add/', 'icon': 'fas fa-plus'},
                        {'name': 'Gestionar Cursos', 'url': '/admin/courses/course/', 'icon': 'fas fa-cog'},
                        {'name': 'Ver Estudiantes', 'url': '/admin/courses/enrollment/', 'icon': 'fas fa-users'},
                    ]
                },
                {
                    'name': 'Análisis',
                    'url': '/admin/',
                    'icon': 'fas fa-chart-bar'
                },
            ]
        else:  # Estudiante
            context['navigation_items'] = [
                {
                    'name': 'Dashboard',
                    'url': '/dashboard/',
                    'icon': 'fas fa-home',
                    'active': request.resolver_match.url_name == 'home'
                },
                {
                    'name': 'Cursos',
                    'url': '/dashboard/search/',
                    'icon': 'fas fa-book',
                    'dropdown': True,
                    'items': []
                },
                {
                    'name': 'Comunidad',
                    'url': '/admin/discussions/',
                    'icon': 'fas fa-users'
                },
            ]

            # Agregar categorías al dropdown de cursos
            for category in context['categories']:
                context['navigation_items'][1]['items'].append({
                    'name': category.name,
                    'url': f'/dashboard/search/?category={category.slug}',
                    'icon': 'fas fa-folder'
                })

            # Agregar separador y "Ver todos"
            if context['categories']:
                context['navigation_items'][1]['items'].append({'divider': True})
                context['navigation_items'][1]['items'].append({
                    'name': 'Ver todos los cursos',
                    'url': '/dashboard/search/',
                    'icon': 'fas fa-list'
                })

    return context


def user_menu_context(request):
    """
    Context processor específico para el menú de usuario
    """
    if not request.user.is_authenticated:
        return {}

    menu_items = [
        {
            'name': 'Mi Perfil',
            'url': f'/users/{request.user.pk}/',
            'icon': 'fas fa-user'
        },
        {
            'name': 'Mis Cursos',
            'url': '/dashboard/search/',
            'icon': 'fas fa-bookmark'
        },
        {
            'name': 'Certificados',
            'url': '/dashboard/certificates/',
            'icon': 'fas fa-certificate'
        },
        {
            'name': 'Configuración',
            'url': f'/users/{request.user.pk}/update/',
            'icon': 'fas fa-cog'
        },
    ]

    # Añadir opciones para profesores
    if request.user.is_teacher:
        menu_items.insert(-1, {
            'name': 'Panel Admin',
            'url': '/admin/',
            'icon': 'fas fa-tools'
        })

    return {
        'user_menu_items': menu_items,
        'user_display_name': request.user.name or request.user.email.split('@')[0],
    }
