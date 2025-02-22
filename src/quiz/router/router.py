from typing import List

from common.db.database import get_db
from common.middleware.auth import get_current_user
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.quiz.schema.schema import (QuestionCreate, QuizCreate,
                                    QuizDetailRequest, QuizDetailResponse,
                                    QuizListRequest, QuizListResponse,
                                    QuizResponse, UpdateQuizSettingsRequest)
from src.quiz.service.service import (add_questions_service,
                                      create_quiz_service,
                                      get_quiz_detail_service,
                                      get_quiz_list_service,
                                      update_quiz_settings_service)
from src.user.model import User

router = APIRouter()

@router.post("/create", response_model=QuizResponse)
def create_quiz(
    quiz_data: QuizCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    **퀴즈 생성 API**  
    - **관리자만 호출 가능**  
    - 제목, 설명을 포함한 퀴즈를 생성  
    - 문제는 생성 후 별도로 추가 가능  
    """
    return create_quiz_service(db, quiz_data, current_user)

@router.put("/{quiz_id}/questions")
def add_questions(
    quiz_id: int,
    questions: list[QuestionCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    **기존 퀴즈에 문제 추가 API**  
    - **관리자만 호출 가능**  
    - 최소 2개 이상의 선택지를 가진 객관식 문제만 추가 가능  
    - 각 문제는 반드시 정답 1개 포함  
    """
    return add_questions_service(db, quiz_id, questions, current_user)

@router.get("/list", response_model=List[QuizListResponse])
def get_quiz_list(
    request: QuizListRequest = Depends(QuizListRequest.as_query), 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    **관리자용 퀴즈 목록 조회 API**  
    - **관리자만 호출 가능**  
    - 전체 퀴즈 목록을 조회 (페이징 처리)  
    - 정렬 기준 및 정렬 방식 지정 가능  
    """
    return get_quiz_list_service(db, request.page, request.page_size, request.sort_by, request.order, current_user)

@router.get("/{quiz_id}", response_model=QuizDetailResponse)
def get_quiz_detail(
    quiz_id: int,
    request: QuizDetailRequest = Depends(QuizDetailRequest.as_query), 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    **관리자용 퀴즈 상세 조회 API**  
    - **관리자만 호출 가능**  
    - 특정 퀴즈의 문제 및 선택지 목록 조회  
    - 문제/선택지 순서는 관리자가 설정한 방식대로 정렬됨  
    """
    return get_quiz_detail_service(db, quiz_id, request, current_user)

@router.patch("/{quiz_id}/settings", response_model=UpdateQuizSettingsRequest)
def update_quiz_settings_api(
    quiz_id: int,
    settings: UpdateQuizSettingsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    **퀴즈 설정 수정 API**  
    - **관리자만 호출 가능**  
    - 문제 랜덤 배치 여부, 선택지 랜덤 배치 여부, 한 페이지당 문제 개수 설정 가능  
    """
    return update_quiz_settings_service(db, quiz_id, settings, current_user)
