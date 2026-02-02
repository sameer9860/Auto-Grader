from django.contrib import admin
from .models import Class, Subject, Student


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'section', 'year', 'teacher']
    list_filter = ['year', 'name']
    search_fields = ['name', 'section']


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'full_marks', 'pass_marks', 'class_level']
    list_filter = ['class_level']
    search_fields = ['name', 'code']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['name', 'roll_no', 'student_class', 'section', 'email']
    list_filter = ['student_class', 'section']
    search_fields = ['name', 'roll_no', 'email']
    readonly_fields = ['created_at', 'updated_at']
