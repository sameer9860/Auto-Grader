from django.db import models
from django.core.validators import MinValueValidator
from accounts.models import CustomUser
from students.models import Class, Subject, Student


class Exam(models.Model):
    """Exam model"""
    
    name = models.CharField(max_length=200, help_text="e.g., First Terminal, Final Exam")
    exam_date = models.DateField()
    student_class = models.ForeignKey(
        Class, 
        on_delete=models.CASCADE, 
        related_name='exams'
    )
    subjects = models.ManyToManyField(Subject, related_name='exams')
    created_by = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE,
        limit_choices_to={'role__in': ['ADMIN', 'TEACHER']}
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.student_class.name}"
    
    class Meta:
        verbose_name = 'Exam'
        verbose_name_plural = 'Exams'
        ordering = ['-exam_date']


class Question(models.Model):
    """Question model with answer keys"""
    
    QUESTION_TYPES = [
        ('MCQ', 'Multiple Choice'),
        ('SHORT', 'Short Answer'),
        ('LONG', 'Long Answer'),
    ]
    
    exam = models.ForeignKey(
        Exam, 
        on_delete=models.CASCADE, 
        related_name='questions'
    )
    subject = models.ForeignKey(
        Subject, 
        on_delete=models.CASCADE,
        related_name='questions'
    )
    question_number = models.IntegerField(validators=[MinValueValidator(1)])
    question_text = models.TextField()
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES)
    marks = models.IntegerField(validators=[MinValueValidator(1)])
    
    # JSONField to store answer key and grading configuration
    # For MCQ: {"correct_answer": "A"}
    # For SHORT/LONG: {
    #     "keywords": ["keyword1", "keyword2"],
    #     "weights": [0.5, 0.5],
    #     "threshold": 0.6,
    #     "expected_answer": "Full answer text"
    # }
    answer_key = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Q{self.question_number}: {self.question_text[:50]}..."
    
    class Meta:
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'
        ordering = ['exam', 'subject', 'question_number']
        unique_together = ['exam', 'subject', 'question_number']


class AnswerSheet(models.Model):
    """Student answer sheet model"""
    
    student = models.ForeignKey(
        Student, 
        on_delete=models.CASCADE,
        related_name='answer_sheets'
    )
    exam = models.ForeignKey(
        Exam, 
        on_delete=models.CASCADE,
        related_name='answer_sheets'
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='answer_sheets'
    )
    
    # JSONField to store student answers
    # Format: {"question_id": "student_answer", ...}
    submitted_answers = models.JSONField(default=dict)
    
    is_graded = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)
    graded_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.student.name} - {self.exam.name} ({self.subject.name})"
    
    class Meta:
        verbose_name = 'Answer Sheet'
        verbose_name_plural = 'Answer Sheets'
        unique_together = ['student', 'exam', 'subject']
        ordering = ['-submitted_at']
