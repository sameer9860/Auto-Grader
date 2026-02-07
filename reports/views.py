from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from students.models import Student, Class
from exams.models import Exam
from grading.models import Result
from accounts.permissions import TeacherRequiredMixin, StudentRequiredMixin


class StudentResultView(StudentRequiredMixin, TemplateView):
    """Individual student result view"""
    template_name = 'reports/student_result.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        student = get_object_or_404(Student, id=self.kwargs['student_id'])
        exam = get_object_or_404(Exam, id=self.kwargs['exam_id'])
        
        results = Result.objects.filter(
            student=student,
            exam=exam
        ).select_related('subject')
        
        context['student'] = student
        context['exam'] = exam
        context['results'] = results
        
        # Calculate overall statistics
        if results:
            total_marks = sum(r.marks_obtained for r in results)
            total_full_marks = sum(r.subject.full_marks for r in results)
            overall_percentage = (total_marks / total_full_marks * 100) if total_full_marks > 0 else 0
            
            context['total_marks'] = total_marks
            context['total_full_marks'] = total_full_marks
            context['overall_percentage'] = overall_percentage
            
            # Get overall grade
            from grading.models import GradingRule
            overall_grade = GradingRule.get_grade_for_percentage(overall_percentage)
            context['overall_grade'] = overall_grade
        
        return context


class ClassResultView(TeacherRequiredMixin, TemplateView):
    """Class-wise result view"""
    template_name = 'reports/class_result.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        student_class = get_object_or_404(Class, id=self.kwargs['class_id'])
        exam = get_object_or_404(Exam, id=self.kwargs['exam_id'])
        
        students = student_class.students.all()
        
        student_results = []
        for student in students:
            results = Result.objects.filter(
                student=student,
                exam=exam
            ).select_related('subject')
            
            if results:
                total_marks = sum(r.marks_obtained for r in results)
                total_full_marks = sum(r.subject.full_marks for r in results)
                percentage = (total_marks / total_full_marks * 100) if total_full_marks > 0 else 0
                
                from grading.models import GradingRule
                grade_rule = GradingRule.get_grade_for_percentage(percentage)
                
                student_results.append({
                    'student': student,
                    'results': results,
                    'total_marks': total_marks,
                    'percentage': percentage,
                    'grade': grade_rule.grade if grade_rule else 'N/A',
                })
        
        context['student_class'] = student_class
        context['exam'] = exam
        context['student_results'] = student_results
        
        return context

class ExamResultListView(TeacherRequiredMixin, ListView):
    """View to list all exams for result viewing"""
    model = Exam
    template_name = 'reports/exam_result_list.html'
    context_object_name = 'exams'
    ordering = ['-exam_date']

