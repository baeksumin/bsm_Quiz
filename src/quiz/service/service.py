from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.quiz.repository.repository import (add_questions_to_quiz, create_quiz,
                                            get_quiz_by_id, get_quiz_detail,
                                            get_quiz_list)
from src.quiz.repository.user_repository import update_quiz_settings
from src.quiz.schema.schema import (QuestionCreate, QuizCreate,
                                    QuizDetailRequest, QuizResponse,
                                    UpdateQuizSettingsRequest,
                                    UpdateQuizSettingsResponse)
from src.user.model import User


def create_quiz_service(db: Session, quiz_data: QuizCreate, current_user: User) -> QuizResponse:
    """관리자만 퀴즈 생성 가능"""
    if not current_user["is_admin"]:
        raise HTTPException(status_code=403, detail="관리자만 퀴즈를 생성할 수 있습니다.")

    new_quiz = create_quiz(db, quiz_data)
    return QuizResponse(id=new_quiz.id, title=new_quiz.title, description=new_quiz.description)


def add_questions_service(db: Session, quiz_id: int, questions: list[QuestionCreate], current_user: User):
    """관리자만 기존 퀴즈에 문제 추가 가능"""
    if not current_user["is_admin"]:
        raise HTTPException(status_code=403, detail="관리자만 문제를 추가할 수 있습니다.")

    quiz = get_quiz_by_id(db, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="해당 퀴즈를 찾을 수 없습니다.")

    return add_questions_to_quiz(db, quiz_id, questions)


def get_quiz_list_service(db: Session, page: int, page_size: int, sort_by: str, order: str, current_user: User):
    """관리자만 전체 퀴즈 목록 조회 가능"""
    if not current_user["is_admin"]:
        raise HTTPException(status_code=403, detail="관리자만 퀴즈 목록을 조회할 수 있습니다.")

    return get_quiz_list(db, page, page_size, sort_by, order)

def get_quiz_detail_service(db: Session, quiz_id: int, request: QuizDetailRequest, current_user: User):
    """관리자만 퀴즈 상세 조회 가능"""
    if not current_user["is_admin"]:
        raise HTTPException(status_code=403, detail="관리자만 퀴즈 상세 조회가 가능합니다.")

    return get_quiz_detail(
        db,
        quiz_id,
        request.page,
        request.page_size,
        request.sort_by,
        request.order
    )

def update_quiz_settings_service(
    db: Session, quiz_id: int, settings: UpdateQuizSettingsRequest, current_user: User
) -> UpdateQuizSettingsResponse:
    """관리자만 퀴즈 설정 변경 가능"""
    if not current_user["is_admin"]:
        raise HTTPException(status_code=403, detail="관리자만 설정을 변경할 수 있습니다.")

    return update_quiz_settings(db, quiz_id, settings)
