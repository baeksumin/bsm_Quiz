from typing import List, Optional

from pydantic import BaseModel, Field


class UserChoiceResponse(BaseModel):
    """사용자용 선택지 응답 (정답 미포함)"""
    id: int
    choice_text: str  

    class Config:
        orm_mode = True

class UserQuestionResponse(BaseModel):
    """사용자용 문제 응답"""
    id: int
    question_text: str
    choices: List[UserChoiceResponse]

    class Config:
        orm_mode = True

class UserQuizDetailResponse(BaseModel):
    """사용자용 퀴즈 상세 응답"""
    id: int
    title: str
    description: Optional[str] = None
    questions: List[UserQuestionResponse]
    current_page: int
    total_pages: int

    class Config:
        orm_mode = True

class QuizRecordResponse(BaseModel):
    id: int
    quiz_id: int
    user_id: int
    score: int

    class Config:
        orm_mode = True

class AnswerSubmit(BaseModel):
    question_id: int
    choice_id: int

class SubmitAnswersRequest(BaseModel):
    answers: List[AnswerSubmit]

class SubmitAnswersResponse(BaseModel):
    id: int
    quiz_id: int
    user_id: int
    score: int

    class Config:
        orm_mode = True

class UserQuizListResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    score: Optional[int] = None  # 응시한 시험이면 점수 표시, 응시 안 했으면 None

    class Config:
        orm_mode = True
