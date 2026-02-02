"""
NLP utilities for probabilistic grading
"""

import re
import string
from typing import List, Dict, Tuple
from collections import Counter
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import Levenshtein


# Common English stopwords
STOPWORDS = {
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've",
    "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his',
    'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself',
    'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom',
    'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were',
    'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did',
    'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
    'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into',
    'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up',
    'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then',
    'once'
}


def preprocess_text(text: str, remove_stopwords: bool = True) -> str:
    """
    Preprocess text by:
    - Converting to lowercase
    - Removing punctuation
    - Removing extra whitespace
    - Optionally removing stopwords
    """
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove stopwords
    if remove_stopwords:
        words = text.split()
        words = [w for w in words if w not in STOPWORDS]
        text = ' '.join(words)
    
    return text


def tokenize(text: str) -> List[str]:
    """Split text into words"""
    return preprocess_text(text).split()


def calculate_levenshtein_distance(str1: str, str2: str) -> int:
    """
    Calculate Levenshtein distance between two strings
    Returns the minimum number of edits needed to transform str1 to str2
    """
    return Levenshtein.distance(str1, str2)


def calculate_levenshtein_similarity(str1: str, str2: str) -> float:
    """
    Calculate similarity ratio using Levenshtein distance
    Returns a value between 0 (completely different) and 1 (identical)
    """
    return Levenshtein.ratio(str1, str2)


def calculate_cosine_similarity(text1: str, text2: str) -> float:
    """
    Calculate cosine similarity between two texts using TF-IDF vectors
    Returns a value between 0 (dissimilar) and 1 (identical)
    """
    if not text1 or not text2:
        return 0.0
    
    try:
        # Preprocess texts
        text1_clean = preprocess_text(text1)
        text2_clean = preprocess_text(text2)
        
        if not text1_clean or not text2_clean:
            return 0.0
        
        # Create TF-IDF vectors
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform([text1_clean, text2_clean])
        
        # Calculate cosine similarity
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        
        return float(similarity)
    except:
        return 0.0


def calculate_keyword_match(
    student_answer: str,
    keywords: List[str],
    weights: List[float] = None
) -> float:
    """
    Calculate keyword matching score
    Returns a weighted score between 0 and 1
    """
    if not keywords or not student_answer:
        return 0.0
    
    # Preprocess student answer
    student_text = preprocess_text(student_answer)
    student_words = set(student_text.split())
    
    # If no weights provided, use equal weights
    if weights is None:
        weights = [1.0 / len(keywords)] * len(keywords)
    
    # Normalize weights
    total_weight = sum(weights)
    if total_weight == 0:
        return 0.0
    weights = [w / total_weight for w in weights]
    
    # Calculate score
    score = 0.0
    for keyword, weight in zip(keywords, weights):
        keyword_clean = preprocess_text(keyword)
        
        # Exact match
        if keyword_clean in student_text:
            score += weight
        # Partial match (fuzzy matching)
        else:
            # Check if keyword appears in any student word with high similarity
            for student_word in student_words:
                similarity = calculate_levenshtein_similarity(keyword_clean, student_word)
                if similarity >= 0.8:  # 80% similarity threshold
                    score += weight * similarity
                    break
    
    return min(score, 1.0)  # Cap at 1.0


def extract_keywords(text: str, top_n: int = 5) -> List[str]:
    """
    Extract top N keywords from text using TF-IDF
    """
    if not text:
        return []
    
    try:
        text_clean = preprocess_text(text)
        words = text_clean.split()
        
        if not words:
            return []
        
        # Use TF-IDF to extract important words
        vectorizer = TfidfVectorizer(max_features=top_n)
        vectorizer.fit([text_clean])
        keywords = vectorizer.get_feature_names_out()
        
        return list(keywords)
    except:
        # Fallback: return most common words
        words = tokenize(text)
        if not words:
            return []
        word_freq = Counter(words)
        return [word for word, _ in word_freq.most_common(top_n)]


def bayesian_inference(
    keyword_score: float,
    similarity_score: float,
    prior_probability: float = 0.5
) -> float:
    """
    Apply Bayesian inference to calculate confidence score
    
    P(Correct|Evidence) = P(Evidence|Correct) * P(Correct) / P(Evidence)
    
    Args:
        keyword_score: Keyword matching score (0-1)
        similarity_score: Cosine similarity score (0-1)
        prior_probability: Prior probability of answer being correct
    
    Returns:
        Confidence score (0-1)
    """
    # Combine evidence (keyword and similarity scores)
    # Using weighted average
    evidence_score = (keyword_score * 0.6 + similarity_score * 0.4)
    
    # P(Evidence|Correct) - likelihood of this evidence given answer is correct
    p_evidence_given_correct = evidence_score
    
    # P(Evidence|Incorrect) - likelihood of this evidence given answer is incorrect
    p_evidence_given_incorrect = 1 - evidence_score
    
    # P(Correct) - prior probability
    p_correct = prior_probability
    
    # P(Incorrect)
    p_incorrect = 1 - prior_probability
    
    # P(Evidence) = P(Evidence|Correct) * P(Correct) + P(Evidence|Incorrect) * P(Incorrect)
    p_evidence = (
        p_evidence_given_correct * p_correct +
        p_evidence_given_incorrect * p_incorrect
    )
    
    if p_evidence == 0:
        return 0.0
    
    # P(Correct|Evidence) = P(Evidence|Correct) * P(Correct) / P(Evidence)
    posterior_probability = (p_evidence_given_correct * p_correct) / p_evidence
    
    return posterior_probability


def calculate_semantic_similarity(text1: str, text2: str) -> float:
    """
    Calculate semantic similarity combining multiple methods
    """
    # Levenshtein similarity
    lev_sim = calculate_levenshtein_similarity(
        preprocess_text(text1),
        preprocess_text(text2)
    )
    
    # Cosine similarity
    cos_sim = calculate_cosine_similarity(text1, text2)
    
    # Combine with weights
    combined_similarity = (lev_sim * 0.4 + cos_sim * 0.6)
    
    return combined_similarity
