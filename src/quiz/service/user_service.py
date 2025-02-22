from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.quiz.model.quiz import Quiz
from src.quiz.repository.user_repository import (create_quiz_record,
                                                 get_quiz_record_by_id,
                                                 get_user_quiz_detail,
                                                 get_user_quiz_list,
                                                 submit_answers)
from src.quiz.schema.user_schema import (QuizRecordResponse,
                                         SubmitAnswersRequest,
                                         SubmitAnswersResponse,
                                         UserQuizListResponse)
from src.user.model import User


def get_user_quiz_list_service(
    db: Session,
    completed: bool,
    current_user: User
) -> List[UserQuizListResponse]:
    return get_user_quiz_list(db, current_user["user_id"], completed)

def get_user_quiz_detail_service(db: Session, quiz_id: int, page: int, current_user: User):
    """사용자가 응시할 퀴즈 상세 조회 서비스 계층"""
    return get_user_quiz_detail(db, quiz_id, page)

def start_quiz_record_service(db: Session, quiz_id: int, current_user: User) -> QuizRecordResponse:
    """사용자가 퀴즈 응시를 시작"""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="퀴즈를 찾을 수 없습니다.")

    record = create_quiz_record(db, quiz_id, current_user["user_id"])
    return QuizRecordResponse(
        id=record.id,
        quiz_id=record.quiz_id,
        user_id=record.user_id,
        score=record.score
    )

def submit_answers_service(
    db: Session,
    quiz_id: int,
    record_id: int,
    answers: SubmitAnswersRequest,
    current_user: User
) -> SubmitAnswersResponse:
    """사용자가 답안을 제출 -> 자동 채점"""
    record = get_quiz_record_by_id(db, record_id)
    if not record or record.quiz_id != quiz_id:
        raise HTTPException(status_code=404, detail="응시 기록을 찾을 수 없습니다.")
    if record.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="본인 응시 기록이 아닙니다.")

    updated_record = submit_answers(db, record, answers)

    return SubmitAnswersResponse(
        id=updated_record.id,
        quiz_id=updated_record.quiz_id,
        user_id=updated_record.user_id,
        score=updated_record.score,
    )

def get_quiz_record_service(db: Session, record_id: int, current_user: User) -> QuizRecordResponse:
    """응시 기록 조회 (본인만 가능)"""
    record = get_quiz_record_by_id(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="응시 기록을 찾을 수 없습니다.")
    if record.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="본인의 응시 기록이 아닙니다.")

    return QuizRecordResponse(
        id=record.id,
        quiz_id=record.quiz_id,
        user_id=record.user_id,
        score=record.score,
    )
