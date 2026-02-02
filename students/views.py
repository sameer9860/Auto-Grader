from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from .models import Student, Class


class StudentListView(LoginRequiredMixin, ListView):
    """List all students"""
    model = Student
    template_name = 'students/student_list.html'
    context_object_name = 'students'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Student.objects.select_related('student_class').all()
        
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
        context['classes'] = Class.objects.all()
        return context


class StudentDetailView(LoginRequiredMixin, DetailView):
    """Student detail view with results"""
    model = Student
    template_name = 'students/student_detail.html'
    context_object_name = 'student'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['results'] = self.object.results.select_related('exam', 'subject').all()
        return context


class StudentCreateView(LoginRequiredMixin, CreateView):
    """Create new student"""
    model = Student
    template_name = 'students/student_form.html'
    fields = ['name', 'roll_no', 'student_class', 'section', 'photo', 'dob', 'address', 'email', 'phone', 'parent_phone']
    success_url = reverse_lazy('students:student_list')


class StudentUpdateView(LoginRequiredMixin, UpdateView):
    """Update student information"""
    model = Student
    template_name = 'students/student_form.html'
    fields = ['name', 'roll_no', 'student_class', 'section', 'photo', 'dob', 'address', 'email', 'phone', 'parent_phone']
    success_url = reverse_lazy('students:student_list')


class ClassListView(LoginRequiredMixin, ListView):
    """List all classes"""
    model = Class
    template_name = 'students/class_list.html'
    context_object_name = 'classes'


class ClassCreateView(LoginRequiredMixin, CreateView):
    """Create new class"""
    model = Class
    template_name = 'students/class_form.html'
    fields = ['name', 'year', 'section', 'teacher']
    success_url = reverse_lazy('students:class_list')
