# core/signals.py (create this file)
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import StudentProfile, FacultyProfile

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'student':
            StudentProfile.objects.create(user=instance)
        elif instance.role == 'faculty':
            FacultyProfile.objects.create(user=instance)
    else:
        # If role changes, you might want to handle profile deletion/creation here
        # Or prevent role changes for existing users with profiles
        pass

# core/apps.py
from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        import core.signals # noqa