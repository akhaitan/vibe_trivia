from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class QuizRequest(BaseModel):
    user_name: str = Field(..., min_length=1, max_length=100)
    topic: str = Field(..., min_length=1, max_length=200)


class Question(BaseModel):
    question: str
    options: List[str] = Field(..., min_items=4, max_items=4)
    correct_answer: str


class QuizResponse(BaseModel):
    quiz_id: str
    questions: List[Question]


class SubmitQuizRequest(BaseModel):
    quiz_id: str
    user_name: str
    answers: List[str] = Field(..., min_items=10, max_items=10)


class QuestionResult(BaseModel):
    question: str
    selected: str
    correct: str
    is_correct: bool


class SubmitQuizResponse(BaseModel):
    score: int
    total: int
    results: List[QuestionResult]
    performance_phrase: str


class QuizAttempt(BaseModel):
    user_name: str
    quiz_topic: str
    score: int
    total: int
    timestamp: datetime


class ScoresResponse(BaseModel):
    attempts: List[QuizAttempt]

