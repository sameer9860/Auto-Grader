from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import CustomUser


class Class(models.Model):
    """Class/Grade model"""
    
    name = models.CharField(max_length=100, help_text="e.g., Grade 10, Class 12")
    year = models.IntegerField(
        validators=[MinValueValidator(2000), MaxValueValidator(2100)],
        help_text="Academic year"
    )
    section = models.CharField(max_length=10, help_text="e.g., A, B, C")
    teacher = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        limit_choices_to={'role': 'TEACHER'},
        related_name='classes_taught'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - Section {self.section} ({self.year})"
    
    class Meta:
        verbose_name = 'Class'
        verbose_name_plural = 'Classes'
        ordering = ['-year', 'name', 'section']
        unique_together = ['name', 'year', 'section']


class Subject(models.Model):
    """Subject model with marks configuration"""
    
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    full_marks = models.IntegerField(validators=[MinValueValidator(1)])
    pass_marks = models.IntegerField(validators=[MinValueValidator(0)])
    class_level = models.ForeignKey(
        Class, 
        on_delete=models.CASCADE, 
        related_name='subjects'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.pass_marks >= self.full_marks:
            raise ValidationError('Pass marks must be less than full marks')
    
    class Meta:
        verbose_name = 'Subject'
        verbose_name_plural = 'Subjects'
        ordering = ['class_level', 'name']


class Student(models.Model):
    """Student model with personal information"""
    
    name = models.CharField(max_length=200)
    roll_no = models.CharField(max_length=50, unique=True)
    student_class = models.ForeignKey(
        Class, 
        on_delete=models.CASCADE, 
        related_name='students'
    )
    section = models.CharField(max_length=10)
    photo = models.ImageField(upload_to='students/', blank=True, null=True)
    dob = models.DateField(verbose_name="Date of Birth")
    address = models.TextField()
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    parent_phone = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.roll_no})"
    
    @property
    def age(self):
        from datetime import date
        today = date.today()
        return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))
    
    class Meta:
        verbose_name = 'Student'
        verbose_name_plural = 'Students'
        ordering = ['student_class', 'roll_no']
