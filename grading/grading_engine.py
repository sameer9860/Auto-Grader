"""
Core grading engine with deterministic and probabilistic grading
"""

from decimal import Decimal
from typing import Dict, Tuple
from .nlp_utils import (
    preprocess_text,
    calculate_keyword_match,
    calculate_cosine_similarity,
    bayesian_inference,
    calculate_semantic_similarity
)
from .models import ProbabilisticGradingConfig


def grade_mcq(question, student_answer: str) -> Tuple[Decimal, Dict]:
    """
    Deterministic grading for Multiple Choice Questions
    
    Args:
        question: Question object
        student_answer: Student's answer
    
    Returns:
        Tuple of (marks_obtained, grading_details)
    """
    grading_details = {
        'question_type': 'MCQ',
        'correct_answer': question.answer_key.get('correct_answer', ''),
        'student_answer': student_answer,
        'is_correct': False
    }
    
    correct_answer = question.answer_key.get('correct_answer', '')
    
    # Exact match (case-insensitive)
    if student_answer.strip().upper() == correct_answer.strip().upper():
        grading_details['is_correct'] = True
        return Decimal(question.marks), grading_details
    
    return Decimal(0), grading_details


def grade_short_answer(
    question,
    student_answer: str,
    config: ProbabilisticGradingConfig = None
) -> Tuple[Decimal, Dict]:
    """
    Probabilistic grading for Short Answer Questions
    
    Uses:
    1. Keyword extraction and matching
    2. Cosine similarity
    3. Bayesian inference
    
    Args:
        question: Question object
        student_answer: Student's answer
        config: Probabilistic grading configuration
    
    Returns:
        Tuple of (marks_obtained, grading_details)
    """
    # Get or create default config
    if config is None:
        config, _ = ProbabilisticGradingConfig.objects.get_or_create(
            name='Default',
            defaults={
                'full_marks_threshold': Decimal('0.70'),
                'partial_marks_threshold': Decimal('0.40'),
                'partial_marks_percentage': Decimal('0.70'),
            }
        )
    
    # Extract answer key data
    answer_key = question.answer_key
    keywords = answer_key.get('keywords', [])
    weights = answer_key.get('weights', None)
    expected_answer = answer_key.get('expected_answer', '')
    
    # Initialize grading details
    grading_details = {
        'question_type': 'SHORT',
        'expected_answer': expected_answer,
        'student_answer': student_answer,
        'keywords': keywords,
        'scores': {}
    }
    
    # If no student answer, return 0
    if not student_answer or not student_answer.strip():
        grading_details['confidence'] = 0.0
        grading_details['marks_category'] = 'no_answer'
        return Decimal(0), grading_details
    
    # Calculate keyword match score
    keyword_score = 0.0
    if config.use_keyword_matching and keywords:
        keyword_score = calculate_keyword_match(student_answer, keywords, weights)
        grading_details['scores']['keyword_score'] = round(keyword_score, 4)
    
    # Calculate similarity score
    similarity_score = 0.0
    if config.use_similarity_scoring and expected_answer:
        similarity_score = calculate_cosine_similarity(student_answer, expected_answer)
        grading_details['scores']['similarity_score'] = round(similarity_score, 4)
    
    # Calculate confidence using Bayesian inference
    if config.use_bayesian_inference:
        confidence = bayesian_inference(keyword_score, similarity_score)
    else:
        # Simple average if Bayesian not used
        confidence = (keyword_score + similarity_score) / 2.0
    
    grading_details['confidence'] = round(confidence, 4)
    
    # Determine marks based on confidence thresholds
    full_marks_threshold = float(config.full_marks_threshold)
    partial_marks_threshold = float(config.partial_marks_threshold)
    partial_marks_pct = float(config.partial_marks_percentage)
    
    if confidence >= full_marks_threshold:
        # Full marks
        marks_obtained = Decimal(question.marks)
        grading_details['marks_category'] = 'full_marks'
    elif confidence >= partial_marks_threshold:
        # Partial marks
        marks_obtained = Decimal(question.marks) * Decimal(str(partial_marks_pct))
        grading_details['marks_category'] = 'partial_marks'
    else:
        # No marks
        marks_obtained = Decimal(0)
        grading_details['marks_category'] = 'no_marks'
    
    return marks_obtained, grading_details


def grade_long_answer(
    question,
    student_answer: str,
    config: ProbabilisticGradingConfig = None
) -> Tuple[Decimal, Dict]:
    """
    Probabilistic grading for Long Answer Questions
    Similar to short answers but with more lenient thresholds
    
    Args:
        question: Question object
        student_answer: Student's answer
        config: Probabilistic grading configuration
    
    Returns:
        Tuple of (marks_obtained, grading_details)
    """
    # Use same logic as short answer for now
    # Can be extended with more sophisticated NLP in the future
    return grade_short_answer(question, student_answer, config)


def grade_question(
    question,
    student_answer: str,
    config: ProbabilisticGradingConfig = None
) -> Tuple[Decimal, Dict]:
    """
    Main grading function that routes to appropriate grading method
    
    Args:
        question: Question object
        student_answer: Student's answer
        config: Probabilistic grading configuration
    
    Returns:
        Tuple of (marks_obtained, grading_details)
    """
    if question.question_type == 'MCQ':
        return grade_mcq(question, student_answer)
    elif question.question_type == 'SHORT':
        return grade_short_answer(question, student_answer, config)
    elif question.question_type == 'LONG':
        return grade_long_answer(question, student_answer, config)
    else:
        # Unknown question type
        return Decimal(0), {'error': 'Unknown question type'}


def grade_answer_sheet(answer_sheet, config: ProbabilisticGradingConfig = None):
    """
    Grade an entire answer sheet
    
    Args:
        answer_sheet: AnswerSheet object
        config: Probabilistic grading configuration
    
    Returns:
        Dict with total marks and detailed grading information
    """
    from exams.models import Question
    from .models import Result
    from django.utils import timezone
    
    # Get all questions for this exam and subject
    questions = Question.objects.filter(
        exam=answer_sheet.exam,
        subject=answer_sheet.subject
    ).order_by('question_number')
    
    total_marks = Decimal(0)
    full_marks = Decimal(0)
    grading_results = []
    
    for question in questions:
        # Get student's answer
        student_answer = answer_sheet.submitted_answers.get(str(question.id), '')
        
        # Grade the question
        marks_obtained, grading_details = grade_question(question, student_answer, config)
        
        total_marks += marks_obtained
        full_marks += Decimal(question.marks)
        
        grading_results.append({
            'question_id': question.id,
            'question_number': question.question_number,
            'marks_obtained': float(marks_obtained),
            'full_marks': question.marks,
            'grading_details': grading_details
        })
    
    # Calculate percentage
    percentage = (total_marks / full_marks * 100) if full_marks > 0 else Decimal(0)
    
    # Create or update result
    result, created = Result.objects.update_or_create(
        student=answer_sheet.student,
        exam=answer_sheet.exam,
        subject=answer_sheet.subject,
        defaults={
            'marks_obtained': total_marks,
            # percentage, grade, gpa will be auto-calculated in Result.save()
        }
    )
    
    # Mark answer sheet as graded
    answer_sheet.is_graded = True
    answer_sheet.graded_at = timezone.now()
    answer_sheet.save()
    
    return {
        'result_id': result.id,
        'total_marks_obtained': float(total_marks),
        'full_marks': float(full_marks),
        'percentage': float(percentage),
        'grade': result.grade,
        'gpa': float(result.gpa),
        'is_pass': result.is_pass,
        'grading_details': grading_results
    }
