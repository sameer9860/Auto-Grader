from django.urls import path
from . import views

app_name = 'grading'

urlpatterns = [
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('auto-grade/<int:answer_sheet_id>/', views.AutoGradeView.as_view(), name='auto_grade'),
    path('bulk-entry/<int:exam_id>/', views.BulkMarkEntryView.as_view(), name='bulk_entry'),
    path('config/', views.GradingConfigView.as_view(), name='grading_config'),
]
