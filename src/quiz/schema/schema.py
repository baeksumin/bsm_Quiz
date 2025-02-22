from datetime import datetime
from typing import List, Optional

from fastapi.param_functions import Query
from pydantic import BaseModel, Field


class ChoiceCreate(BaseModel):
    choice_text: str
    is_correct: bool

class QuestionCreate(BaseModel):
    question_text: str
    choices: List[ChoiceCreate]  # 문제에 대한 선택지 리스트

    @classmethod
    def validate_choices(cls, values):
        """선택지는 최소 2개 이상이어야 하며, 정답이 반드시 1개여야 함."""
        choices = values.get("choices", [])
        if len(choices) < 2:
            raise ValueError("각 문제는 최소 2개의 선택지를 가져야 합니다.")
        correct_answers = sum(1 for choice in choices if choice.is_correct)
        if correct_answers < 1:
            raise ValueError("각 문제에는 반드시 정답이 1개 포함되어야 합니다.")
        return values

class QuizCreate(BaseModel):
    title: str
    description: str = None
    questions: List[QuestionCreate]  # 퀴즈에 포함될 문제 리스트
    questions_per_page: Optional[int] = 10  

class QuizResponse(BaseModel):
    id: int
    title: str
    description: str

    class Config:
        orm_mode = True
        from_attributes=True

class QuizListRequest(BaseModel):
    page: int = 1
    page_size: int = 10
    sort_by: str = "created_at"
    order: str = "desc"
    
    @classmethod
    def as_query(
        cls,
        page: int = Query(1, alias="page"),
        page_size: int = Query(10, alias="page_size"),
        sort_by: str = Query("created_at", alias="sort_by"),
        order: str = Query("desc", alias="order"),
    ):
        """Query Parameters를 Pydantic 모델로 변환하는 헬퍼 메서드"""
        return cls(page=page, page_size=page_size, sort_by=sort_by, order=order)

class QuizListResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    created_at: datetime
    num_questions: int  # 포함된 문제 개수

    class Config:
        orm_mode = True
        from_attributes=True

class QuizDetailRequest(BaseModel):
    """퀴즈 상세 조회 요청 (Query Parameters)"""
    page: int = 1
    page_size: int = 10
    sort_by: str = "created_at"
    order: str = "desc"

    @classmethod
    def as_query(
        cls,
        page: int = Query(1, alias="page"),
        page_size: int = Query(10, alias="page_size"),
        sort_by: str = Query("created_at", alias="sort_by"),
        order: str = Query("desc", alias="order"),
    ):
        return cls(page=page, page_size=page_size, sort_by=sort_by, order=order)

class ChoiceResponse(BaseModel):
    """선택지 응답"""
    id: int
    choice_text: str
    is_correct: bool  # 관리자 조회이므로 정답 포함

    class Config:
        orm_mode = True
        from_attributes=True

class QuestionResponse(BaseModel):
    """문제 응답"""
    id: int
    question_text: str
    choices: List[ChoiceResponse]

    class Config:
        orm_mode = True
        from_attributes=True

class QuizDetailResponse(BaseModel):
    """퀴즈 상세 응답"""
    id: int
    title: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    total_questions: int
    questions: List[QuestionResponse]

    class Config:
        orm_mode = True
        from_attributes=True

class UpdateQuizSettingsRequest(BaseModel):
    """관리자가 퀴즈 설정을 변경할 때 사용하는 요청 모델"""
    is_random_questions: Optional[bool] = None
    is_random_choices: Optional[bool] = None
    questions_per_page: Optional[int] = None

class UpdateQuizSettingsResponse(BaseModel):
    """퀴즈 설정 변경 후 응답 모델"""
    id: int
    title: str
    is_random_questions: bool
    is_random_choices: bool
    questions_per_page: int

    class Config:
        orm_mode = True
        from_attributes=True
