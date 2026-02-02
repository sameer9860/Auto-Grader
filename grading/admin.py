from django.contrib import admin
from .models import GradingRule, Result, ProbabilisticGradingConfig


@admin.register(GradingRule)
class GradingRuleAdmin(admin.ModelAdmin):
    list_display = ['grade', 'min_percentage', 'max_percentage', 'gpa', 'description']
    ordering = ['-min_percentage']


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'exam', 'subject', 'marks_obtained', 'percentage', 'grade', 'is_pass']
    list_filter = ['exam', 'subject', 'grade', 'is_pass']
    search_fields = ['student__name', 'student__roll_no']
    readonly_fields = ['percentage', 'grade', 'gpa', 'is_pass', 'generated_at', 'updated_at']


@admin.register(ProbabilisticGradingConfig)
class ProbabilisticGradingConfigAdmin(admin.ModelAdmin):
    list_display = ['name', 'full_marks_threshold', 'partial_marks_threshold', 'partial_marks_percentage']
    fields = [
        'name',
        'full_marks_threshold',
        'partial_marks_threshold',
        'partial_marks_percentage',
        'use_keyword_matching',
        'use_similarity_scoring',
        'use_bayesian_inference',
    ]
