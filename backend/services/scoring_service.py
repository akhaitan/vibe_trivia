from typing import List, Tuple
from backend.models import Question, QuestionResult


class ScoringService:
    """Service for calculating quiz scores and generating results."""
    
    def calculate_score(
        self,
        questions: List[Question],
        answers: List[str]
    ) -> Tuple[int, List[QuestionResult]]:
        """
        Calculate score and generate detailed results.
        
        Args:
            questions: List of Question objects with correct answers
            answers: List of user-selected answers (one per question)
            
        Returns:
            Tuple of (score, results_list)
        """
        if len(questions) != len(answers):
            raise ValueError("Number of questions and answers must match")
        
        score = 0
        results = []
        
        for i, question in enumerate(questions):
            selected = answers[i]
            correct = question.correct_answer
            is_correct = selected == correct
            
            if is_correct:
                score += 1
            
            results.append(QuestionResult(
                question=question.question,
                selected=selected,
                correct=correct,
                is_correct=is_correct
            ))
        
        return score, results

