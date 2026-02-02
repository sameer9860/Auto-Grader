from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from students.models import Student, Subject
from exams.models import Exam


class GradingRule(models.Model):
    """Nepal grading scale configuration"""
    
    grade = models.CharField(max_length=5, unique=True)
    min_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))]
    )
    max_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))]
    )
    description = models.CharField(max_length=100)
    gpa = models.DecimalField(
        max_digits=3, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('4'))]
    )
    
    def __str__(self):
        return f"{self.grade} ({self.min_percentage}% - {self.max_percentage}%)"
    
    @classmethod
    def get_grade_for_percentage(cls, percentage):
        """Get grade based on percentage"""
        try:
            rule = cls.objects.filter(
                min_percentage__lte=percentage,
                max_percentage__gte=percentage
            ).first()
            return rule if rule else None
        except:
            return None
    
    class Meta:
        verbose_name = 'Grading Rule'
        verbose_name_plural = 'Grading Rules'
        ordering = ['-min_percentage']


class Result(models.Model):
    """Student result model"""
    
    student = models.ForeignKey(
        Student, 
        on_delete=models.CASCADE,
        related_name='results'
    )
    exam = models.ForeignKey(
        Exam, 
        on_delete=models.CASCADE,
        related_name='results'
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='results'
    )
    
    marks_obtained = models.DecimalField(
        max_digits=6, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))]
    )
    percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))]
    )
    grade = models.CharField(max_length=5)
    gpa = models.DecimalField(
        max_digits=3, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('4'))]
    )
    
    is_pass = models.BooleanField(default=False)
    remarks = models.TextField(blank=True, null=True)
    
    generated_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.student.name} - {self.exam.name} ({self.subject.name}): {self.grade}"
    
    def save(self, *args, **kwargs):
        # Calculate percentage
        if self.subject.full_marks > 0:
            self.percentage = (self.marks_obtained / self.subject.full_marks) * 100
        
        # Determine grade
        grading_rule = GradingRule.get_grade_for_percentage(self.percentage)
        if grading_rule:
            self.grade = grading_rule.grade
            self.gpa = grading_rule.gpa
        
        # Check if passed
        self.is_pass = self.marks_obtained >= self.subject.pass_marks
        
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'Result'
        verbose_name_plural = 'Results'
        unique_together = ['student', 'exam', 'subject']
        ordering = ['-generated_at']


class ProbabilisticGradingConfig(models.Model):
    """Configuration for probabilistic grading thresholds"""
    
    name = models.CharField(max_length=100, unique=True)
    full_marks_threshold = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('0.70'),
        help_text="Confidence threshold for full marks (default: 0.70)"
    )
    partial_marks_threshold = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('0.40'),
        help_text="Confidence threshold for partial marks (default: 0.40)"
    )
    partial_marks_percentage = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('0.70'),
        help_text="Percentage of marks to award for partial match (default: 70%)"
    )
    
    use_keyword_matching = models.BooleanField(default=True)
    use_similarity_scoring = models.BooleanField(default=True)
    use_bayesian_inference = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Probabilistic Grading Config'
        verbose_name_plural = 'Probabilistic Grading Configs'
