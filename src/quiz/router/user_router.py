from typing import List

from common.db.database import get_db
from common.middleware.auth import get_current_user
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from src.quiz.schema.user_schema import (QuizRecordResponse,
                                         SubmitAnswersRequest,
                                         SubmitAnswersResponse,
                                         UserQuizDetailResponse,
                                         UserQuizListResponse)
from src.quiz.service.user_service import (get_quiz_record_service,
                                           get_user_quiz_detail_service,
                                           get_user_quiz_list_service,
                                           start_quiz_record_service,
                                           submit_answers_service)
from src.user.model import User

router = APIRouter()


@router.get("/list", response_model=List[UserQuizListResponse])
def get_user_quiz_list_api(
    completed: bool = Query(False, alias="completed"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    **사용자용 퀴즈 목록 조회 API**  
    - `completed=true`  → '응시한 시험' 목록 조회  
    - `completed=false` → '응시하지 않은 시험' 목록 조회  
    - 응시 여부에 따라 필터링된 퀴즈 리스트 제공  
    """
    return get_user_quiz_list_service(db, completed, current_user)
    
@router.get("/{quiz_id}", response_model=UserQuizDetailResponse)
def get_user_quiz_detail(
    quiz_id: int,
    page: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    **사용자용 퀴즈 상세 조회 API**  
    - **응시할 시험의 문제 및 선택지 제공**  
    - **정답 정보는 포함되지 않음**  
    - 관리자가 설정한 랜덤 배치에 따라 문제/선택지 순서가 변경될 수 있음  
    """
    return get_user_quiz_detail_service(db, quiz_id, page, current_user)

@router.post("/{quiz_id}/attempt", response_model=QuizRecordResponse)
def start_quiz_record(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    **퀴즈 응시 시작 API**  
    - **사용자가 퀴즈를 응시 시작하면 새로운 응시 기록(quiz_record) 생성**  
    - 퀴즈를 시작해야 답안을 제출할 수 있음  
    """
    return start_quiz_record_service(db, quiz_id, current_user)

@router.post("/{quiz_id}/attempt/{attempt_id}/submit", response_model=SubmitAnswersResponse)
def submit_quiz_answers(
    quiz_id: int,
    attempt_id: int,
    request: SubmitAnswersRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    **퀴즈 답안 제출 API**  
    - 사용자가 답안을 제출하면 즉시 자동 채점됨  
    - 점수는 `(정답 개수 / 전체 문제 수) * 100` 방식으로 계산됨  
    - 응시 기록(quiz_record)에 점수가 저장됨  
    """
    return submit_answers_service(db, quiz_id, attempt_id, request, current_user)

@router.get("/attempt/{attempt_id}", response_model=QuizRecordResponse)
def get_quiz_record(
    attempt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    **퀴즈 응시 기록 조회 API**  
    - **사용자 본인의 응시 기록만 조회 가능**  
    - 응시한 퀴즈의 점수 및 제출한 답안 정보를 확인 가능  
    """
    return get_quiz_record_service(db, attempt_id, current_user)
