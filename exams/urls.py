from django.urls import path
from . import views

app_name = 'exams'

urlpatterns = [
    path('', views.ExamListView.as_view(), name='exam_list'),
    path('add/', views.ExamCreateView.as_view(), name='exam_add'),
    path('<int:pk>/', views.ExamDetailView.as_view(), name='exam_detail'),
]
