from django.urls import path
from . import views

app_name = 'exams'

urlpatterns = [
    path('', views.ExamListView.as_view(), name='exam_list'),
    path('add/', views.ExamCreateView.as_view(), name='exam_add'),
    path('<int:pk>/', views.ExamDetailView.as_view(), name='exam_detail'),
    path('<int:exam_id>/question/add/', views.QuestionCreateView.as_view(), name='question_add'),
    path('<int:exam_id>/take/', views.AnswerSheetCreateView.as_view(), name='take_exam'),
]
