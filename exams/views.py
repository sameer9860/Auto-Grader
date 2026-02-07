from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Exam, Question, AnswerSheet
from students.models import Subject
from accounts.permissions import TeacherRequiredMixin, StudentRequiredMixin


class ExamListView(LoginRequiredMixin, ListView):
    """List all exams"""
    model = Exam
    template_name = 'exams/exam_list.html'
    context_object_name = 'exams'
    paginate_by = 20
    ordering = ['-exam_date']


class ExamDetailView(LoginRequiredMixin, DetailView):
    """Exam detail view with questions"""
    model = Exam
    template_name = 'exams/exam_detail.html'
    context_object_name = 'exam'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['questions'] = self.object.questions.select_related('subject').order_by('question_number')
        return context


class ExamCreateView(TeacherRequiredMixin, CreateView):
    """Create new exam"""
    model = Exam
    template_name = 'exams/exam_form.html'
    fields = ['name', 'exam_date', 'student_class', 'subjects']
    success_url = reverse_lazy('exams:exam_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class QuestionCreateView(TeacherRequiredMixin, CreateView):
    """Add question to exam"""
    model = Question
    template_name = 'exams/question_form.html'
    fields = ['subject', 'question_number', 'question_text', 'question_type', 'marks', 'answer_key']
    
    def dispatch(self, request, *args, **kwargs):
        self.exam = get_object_or_404(Exam, pk=kwargs['exam_id'])
        return super().dispatch(request, *args, **kwargs)
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['exam'] = self.exam
        return context
        
    def form_valid(self, form):
        form.instance.exam = self.exam
        return super().form_valid(form)
        
    def get_success_url(self):
        return reverse('exams:exam_detail', kwargs={'pk': self.exam.pk})


class AnswerSheetCreateView(StudentRequiredMixin, CreateView):
    """Simulate taking an exam / submitting answers"""
    model = AnswerSheet
    template_name = 'exams/take_exam.html'
    fields = ['student'] # We'll handle questions manually
    
    def dispatch(self, request, *args, **kwargs):
        self.exam = get_object_or_404(Exam, pk=kwargs['exam_id'])
        return super().dispatch(request, *args, **kwargs)
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['exam'] = self.exam
        context['questions'] = self.exam.questions.all().order_by('question_number')
        # Filter students who belong to this class
        context['students'] = self.exam.student_class.students.all()
        return context
        
    def form_valid(self, form):
        form.instance.exam = self.exam
        
        # Set subject from POST
        subject_id = self.request.POST.get('subject')
        if subject_id:
            form.instance.subject_id = subject_id
        
        # Construct answers JSON
        answers = {}
        for key, value in self.request.POST.items():
            if key.startswith('question_'):
                q_id = key.split('_')[1]
                answers[q_id] = value
        
        form.instance.submitted_answers = answers
        return super().form_valid(form)
        
    def get_success_url(self):
        return reverse('grading:auto_grade', kwargs={'answer_sheet_id': self.object.id})

