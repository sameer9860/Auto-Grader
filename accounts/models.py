from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Custom user model with role-based access"""
    
    ROLE_CHOICES = [
        ('ADMIN', 'Administrator'),
        ('TEACHER', 'Teacher'),
        ('STUDENT', 'Student'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='STUDENT')
    roll_no = models.CharField(max_length=50, blank=True, null=True, help_text="For students, enter their roll number to link results")
    phone = models.CharField(max_length=15, blank=True, null=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
