from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.ExamResultListView.as_view(), name='exam_result_list'),
    path('student/<int:student_id>/exam/<int:exam_id>/', views.StudentResultView.as_view(), name='student_result'),
    path('class/<int:class_id>/exam/<int:exam_id>/', views.ClassResultView.as_view(), name='class_result'),
]
