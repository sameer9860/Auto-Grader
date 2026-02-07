from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from .models import Student, Class
from accounts.permissions import TeacherRequiredMixin


class StudentListView(TeacherRequiredMixin, ListView):
    """List all students"""
    model = Student
    template_name = 'students/student_list.html'
    context_object_name = 'students'
    paginate_by = 20
    
    def get_queryset(self):
        user = self.request.user
        queryset = Student.objects.select_related('student_class').all()
        
        # Data isolation: Teacher only sees students in their own classes
        if user.role == 'TEACHER':
            queryset = queryset.filter(student_class__teacher=user)
        
        # Filter by class if specified
        class_id = self.request.GET.get('class_id')
        if class_id:
            queryset = queryset.filter(student_class_id=class_id)
        
        # Search by name or roll number
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(name__icontains=search) | 
                models.Q(roll_no__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.role == 'TEACHER':
            context['classes'] = Class.objects.filter(teacher=user)
        else:
            context['classes'] = Class.objects.all()
        return context


class StudentDetailView(TeacherRequiredMixin, DetailView):
    """Student detail view with results"""
    model = Student
    template_name = 'students/student_detail.html'
    context_object_name = 'student'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Students should not access this view based on mixin, but safety check if student role added
        if self.request.user.role == 'STUDENT' and self.object.email != self.request.user.email:
            raise PermissionDenied
        
        context['results'] = self.object.results.select_related('exam', 'subject').all()
        return context


class StudentCreateView(TeacherRequiredMixin, CreateView):
    """Create new student"""
    model = Student
    template_name = 'students/student_form.html'
    fields = ['name', 'roll_no', 'student_class', 'section', 'photo', 'dob', 'address', 'email', 'phone', 'parent_phone']
    success_url = reverse_lazy('students:student_list')


class StudentUpdateView(TeacherRequiredMixin, UpdateView):
    """Update student information"""
    model = Student
    template_name = 'students/student_form.html'
    fields = ['name', 'roll_no', 'student_class', 'section', 'photo', 'dob', 'address', 'email', 'phone', 'parent_phone']
    success_url = reverse_lazy('students:student_list')


class ClassListView(TeacherRequiredMixin, ListView):
    """List all classes"""
    model = Class
    template_name = 'students/class_list.html'
    context_object_name = 'classes'

    def get_queryset(self):
        user = self.request.user
        if user.role == 'TEACHER':
            return Class.objects.filter(teacher=user)
        return Class.objects.all()


class ClassCreateView(TeacherRequiredMixin, CreateView):
    """Create new class"""
    model = Class
    template_name = 'students/class_form.html'
    fields = ['name', 'year', 'section', 'teacher']
    success_url = reverse_lazy('students:class_list')
