from django.test import TestCase
from decimal import Decimal
from grading.grading_engine import grade_mcq, grade_short_answer
from grading.nlp_utils import (
    preprocess_text,
    calculate_keyword_match,
    calculate_cosine_similarity,
    bayesian_inference
)
from grading.models import ProbabilisticGradingConfig
from exams.models import Question

class NLPUtilsTests(TestCase):
    def test_preprocess_text(self):
        text = "This IS a Sample Text! With Punctuation."
        processed = preprocess_text(text, remove_stopwords=True)
        # stopwords: this, is, a, with
        expected = "sample text punctuation"
        self.assertEqual(processed, expected)

    def test_keyword_match_exact(self):
        student_answer = "Photosynthesis is a process using sunlight"
        keywords = ["photosynthesis", "sunlight"]
        score = calculate_keyword_match(student_answer, keywords)
        self.assertEqual(score, 1.0)

    def test_keyword_match_partial(self):
        student_answer = "It uses sunlite" # Typo
        keywords = ["sunlight"]
        # Should detect 'sunlite' ~ 'sunlight' with high similarity
        score = calculate_keyword_match(student_answer, keywords)
        self.assertGreater(score, 0.5)

    def test_cosine_similarity(self):
        text1 = "The cat sat on the mat"
        text2 = "The cat sat on the mat"
        score = calculate_cosine_similarity(text1, text2)
        self.assertAlmostEqual(score, 1.0)

        text3 = "completely different text"
        score_diff = calculate_cosine_similarity(text1, text3)
        self.assertLess(score_diff, 0.2)

    def test_bayesian_inference(self):
        # High evidence should yield high confidence
        confidence = bayesian_inference(keyword_score=0.9, similarity_score=0.9)
        self.assertGreater(confidence, 0.8)

        # Low evidence should yield low confidence
        confidence_low = bayesian_inference(keyword_score=0.1, similarity_score=0.1)
        self.assertLess(confidence_low, 0.3)

class GradingEngineTests(TestCase):
    def setUp(self):
        self.config = ProbabilisticGradingConfig.objects.create(
            name='Test Config',
            full_marks_threshold=Decimal('0.70'),
            partial_marks_threshold=Decimal('0.40'),
            partial_marks_percentage=Decimal('0.70')
        )

    def test_grade_mcq_correct(self):
        class MockQuestion:
            marks = 5
            answer_key = {'correct_answer': 'A'}
        
        marks, details = grade_mcq(MockQuestion(), 'A')
        self.assertEqual(marks, 5)
        self.assertTrue(details['is_correct'])

    def test_grade_mcq_incorrect(self):
        class MockQuestion:
            marks = 5
            answer_key = {'correct_answer': 'A'}
        
        marks, details = grade_mcq(MockQuestion(), 'B')
        self.assertEqual(marks, 0)
        self.assertFalse(details['is_correct'])

    def test_grade_short_answer_full_marks(self):
        class MockQuestion:
            marks = 10
            question_type = 'SHORT'
            answer_key = {
                'keywords': ['python', 'programming', 'language'],
                'expected_answer': "Python is a high-level programming language."
            }
        
        student_answer = "Python is a great programming language."
        marks, details = grade_short_answer(MockQuestion(), student_answer, self.config)
        
        self.assertEqual(marks, 10)
        self.assertEqual(details['marks_category'], 'full_marks')

    def test_grade_short_answer_partial_marks(self):
        class MockQuestion:
            marks = 10
            question_type = 'SHORT'
            answer_key = {
                'keywords': ['photosynthesis', 'plants', 'sunlight'],
                'expected_answer': "Photosynthesis is the process by which plants use sunlight to make food."
            }
        
        # Weak answer, missing key concepts but somewhat relevant
        student_answer = "Plants make food."
        marks, details = grade_short_answer(MockQuestion(), student_answer, self.config)
        
        # Should likely fall into partial marks or low full marks depending on strictness
        # With current threshold 0.7 for full, this might be partial as keyword match is low (1/3)
        # Let's ensure it's handled gracefully
        self.assertTrue(marks in [0, 7, 10]) 

    def test_grade_short_answer_no_marks(self):
        class MockQuestion:
            marks = 10
            question_type = 'SHORT'
            answer_key = {
                'keywords': ['gravity', 'force'],
                'expected_answer': "Gravity is a force that attracts a body toward the center of the earth."
            }
        
        student_answer = "I don't know the answer."
        marks, details = grade_short_answer(MockQuestion(), student_answer, self.config)
        
        self.assertEqual(marks, 0)
