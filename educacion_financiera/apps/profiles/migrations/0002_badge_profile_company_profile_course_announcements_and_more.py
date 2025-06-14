# Generated by Django 5.1.9 on 2025-05-29 20:46

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Badge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('description', models.TextField(verbose_name='Description')),
                ('icon', models.CharField(help_text='Font Awesome icon class', max_length=100, verbose_name='Icon Class')),
                ('badge_type', models.CharField(choices=[('completion', 'Course Completion'), ('streak', 'Learning Streak'), ('time', 'Study Time'), ('engagement', 'Community Engagement'), ('special', 'Special Achievement')], max_length=20, verbose_name='Badge Type')),
                ('color', models.CharField(default='primary', max_length=20, verbose_name='Color')),
                ('required_value', models.PositiveIntegerField(help_text='Minimum value required to earn this badge', verbose_name='Required Value')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
            ],
            options={
                'verbose_name': 'Badge',
                'verbose_name_plural': 'Badges',
                'ordering': ['badge_type', 'required_value'],
            },
        ),
        migrations.AddField(
            model_name='profile',
            name='company',
            field=models.CharField(blank=True, max_length=200, verbose_name='Company'),
        ),
        migrations.AddField(
            model_name='profile',
            name='course_announcements',
            field=models.BooleanField(default=True, verbose_name='Course announcements'),
        ),
        migrations.AddField(
            model_name='profile',
            name='courses_completed',
            field=models.PositiveIntegerField(default=0, verbose_name='Courses Completed'),
        ),
        migrations.AddField(
            model_name='profile',
            name='current_streak',
            field=models.PositiveIntegerField(default=0, verbose_name='Current Streak (days)'),
        ),
        migrations.AddField(
            model_name='profile',
            name='experience_level',
            field=models.CharField(choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')], default='beginner', max_length=20, verbose_name='Experience Level'),
        ),
        migrations.AddField(
            model_name='profile',
            name='experience_years',
            field=models.PositiveIntegerField(default=0, verbose_name='Years of Experience'),
        ),
        migrations.AddField(
            model_name='profile',
            name='interests',
            field=models.TextField(blank=True, help_text='Comma-separated list of financial topics of interest', verbose_name='Interests'),
        ),
        migrations.AddField(
            model_name='profile',
            name='last_activity',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Last Activity'),
        ),
        migrations.AddField(
            model_name='profile',
            name='longest_streak',
            field=models.PositiveIntegerField(default=0, verbose_name='Longest Streak (days)'),
        ),
        migrations.AddField(
            model_name='profile',
            name='marketing_emails',
            field=models.BooleanField(default=False, verbose_name='Marketing emails'),
        ),
        migrations.AddField(
            model_name='profile',
            name='public_profile',
            field=models.BooleanField(default=True, verbose_name='Public profile'),
        ),
        migrations.AddField(
            model_name='profile',
            name='title',
            field=models.CharField(blank=True, max_length=200, verbose_name='Professional Title'),
        ),
        migrations.AddField(
            model_name='profile',
            name='total_study_time',
            field=models.PositiveIntegerField(default=0, help_text='Total time spent studying in minutes', verbose_name='Total Study Time (minutes)'),
        ),
        migrations.AddField(
            model_name='profile',
            name='youtube',
            field=models.CharField(blank=True, max_length=100, verbose_name='YouTube'),
        ),
        migrations.CreateModel(
            name='UserBadge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('earned_at', models.DateTimeField(auto_now_add=True, verbose_name='Earned At')),
                ('is_featured', models.BooleanField(default=False, verbose_name='Is Featured')),
                ('badge', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='earned_by', to='profiles.badge', verbose_name='Badge')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='earned_badges', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'User Badge',
                'verbose_name_plural': 'User Badges',
                'ordering': ['-earned_at'],
                'unique_together': {('user', 'badge')},
            },
        ),
    ]
