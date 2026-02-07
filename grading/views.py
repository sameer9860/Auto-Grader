from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Count, Avg
from decimal import Decimal
from .models import Result, GradingRule, ProbabilisticGradingConfig
from exams.models import Exam, AnswerSheet
from students.models import Student
from .grading_engine import grade_answer_sheet
from accounts.permissions import AdminRequiredMixin, TeacherRequiredMixin


class DashboardView(LoginRequiredMixin, TemplateView):
    """Main dashboard view"""
    template_name = 'grading/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        if user.role in ['ADMIN', 'TEACHER']:
            # Statistics for staff
            context['total_students'] = Student.objects.count()
            context['total_exams'] = Exam.objects.count()
            context['total_results'] = Result.objects.count()
            
            # Recent results for staff
            context['recent_results'] = Result.objects.select_related(
                'student', 'exam', 'subject'
            ).order_by('-generated_at')[:10]
            
            # Grade distribution for staff
            grade_stats = Result.objects.values('grade').annotate(
                count=Count('id')
            ).order_by('-count')
            context['grade_stats'] = grade_stats
        else:
            # Statistics for student
            # Try to find the student record linked to this user (if any)
            # For now, we'll try matching by email
            student = Student.objects.filter(email=user.email).first()
            if student:
                student_results = Result.objects.filter(student=student)
                context['total_exams'] = student_results.values('exam').distinct().count()
                context['total_results'] = student_results.count()
                context['recent_results'] = student_results.select_related(
                    'exam', 'subject'
                ).order_by('-generated_at')[:10]
                
                grade_stats = student_results.values('grade').annotate(
                    count=Count('id')
                ).order_by('-count')
                context['grade_stats'] = grade_stats
                context['student_record'] = student
            else:
                context['no_student_linked'] = True
        
        return context


class AutoGradeView(LoginRequiredMixin, TemplateView):
    """Auto grade an answer sheet"""
    template_name = 'grading/auto_grade_result.html'
    
    def get(self, request, answer_sheet_id):
        answer_sheet = get_object_or_404(AnswerSheet, id=answer_sheet_id)
        
        # Get grading config
        config = ProbabilisticGradingConfig.objects.filter(name='Default').first()
        
        # Grade the answer sheet
        grading_result = grade_answer_sheet(answer_sheet, config)
        
        messages.success(request, 'Answer sheet graded successfully!')
        
        context = {
            'answer_sheet': answer_sheet,
            'grading_result': grading_result,
        }
        
        return render(request, self.template_name, context)


class BulkMarkEntryView(TeacherRequiredMixin, TemplateView):
    """Bulk mark entry for an exam"""
    template_name = 'grading/bulk_entry.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        exam_id = self.kwargs.get('exam_id')
        exam = get_object_or_404(Exam, id=exam_id)
        context['exam'] = exam
        context['students'] = exam.student_class.students.all()
        context['subjects'] = exam.subjects.all()
        return context
    def post(self, request, *args, **kwargs):
        exam_id = self.kwargs.get('exam_id')
        exam = get_object_or_404(Exam, id=exam_id)
        students = exam.student_class.students.all()
        subjects = exam.subjects.all()
        
        for student in students:
            for subject in subjects:
                # Key format: mark_studentId_subjectId
                key = f'mark_{student.id}_{subject.id}'
                mark_value = request.POST.get(key)
                
                if mark_value and mark_value.strip():
                    try:
                        marks = Decimal(mark_value)
                        
                        # Update or create result
                        result, created = Result.objects.update_or_create(
                            student=student,
                            exam=exam,
                            subject=subject,
                            defaults={'marks_obtained': marks}
                        )
                        result.save() # Trigger save to calculate grade
                        
                    except Exception as e:
                        # Log error or handle gracefully
                        pass
        
        messages.success(request, 'Marks saved successfully!')
        return redirect('exams:exam_list')


class GradingConfigView(AdminRequiredMixin, ListView):
    """View and manage grading configurations"""
    model = ProbabilisticGradingConfig
    template_name = 'grading/config.html'
    context_object_name = 'configs'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['grading_rules'] = GradingRule.objects.all()
        return context
