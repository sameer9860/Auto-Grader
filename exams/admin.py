from django.contrib import admin
from .models import Exam, Question, AnswerSheet


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ['question_number', 'subject', 'question_type', 'marks']


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['name', 'student_class', 'exam_date', 'created_by']
    list_filter = ['exam_date', 'student_class']
    search_fields = ['name']
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_number', 'exam', 'subject', 'question_type', 'marks']
    list_filter = ['exam', 'subject', 'question_type']
    search_fields = ['question_text']


@admin.register(AnswerSheet)
class AnswerSheetAdmin(admin.ModelAdmin):
    list_display = ['student', 'exam', 'subject', 'is_graded', 'submitted_at']
    list_filter = ['exam', 'subject', 'is_graded']
    search_fields = ['student__name', 'student__roll_no']
    readonly_fields = ['submitted_at', 'graded_at']
