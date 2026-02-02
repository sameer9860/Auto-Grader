from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Exam


class ExamListView(LoginRequiredMixin, ListView):
    """List all exams"""
    model = Exam
    template_name = 'exams/exam_list.html'
    context_object_name = 'exams'
    paginate_by = 20


class ExamDetailView(LoginRequiredMixin, DetailView):
    """Exam detail view with questions"""
    model = Exam
    template_name = 'exams/exam_detail.html'
    context_object_name = 'exam'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['questions'] = self.object.questions.select_related('subject').all()
        return context


class ExamCreateView(LoginRequiredMixin, CreateView):
    """Create new exam"""
    model = Exam
    template_name = 'exams/exam_form.html'
    fields = ['name', 'exam_date', 'student_class', 'subjects']
    success_url = reverse_lazy('exams:exam_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)
