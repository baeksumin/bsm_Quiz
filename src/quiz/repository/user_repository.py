import random
from typing import List

import pytz
from fastapi.exceptions import HTTPException
from sqlalchemy import desc, func
from sqlalchemy.orm import Session
from src.quiz.model import Choice, Question, Quiz
from src.quiz.model.answer import Answer
from src.quiz.model.quiz_record import QuizRecord
from src.quiz.schema.schema import (UpdateQuizSettingsRequest,
                                    UpdateQuizSettingsResponse)
from src.quiz.schema.user_schema import (SubmitAnswersRequest,
                                         UserChoiceResponse,
                                         UserQuestionResponse,
                                         UserQuizDetailResponse,
                                         UserQuizListResponse)

KST = pytz.timezone("Asia/Seoul")


def get_user_quiz_detail(db: Session, quiz_id: int, page: int) -> UserQuizDetailResponse:
    """사용자가 응시할 퀴즈 상세 조회 (정답 미포함 & 랜덤 배치)"""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="해당 퀴즈를 찾을 수 없습니다.")

    # 1) 페이지당 문항 수 확인
    page_size = quiz.questions_per_page

    # 2) 전체 문항 개수
    total_questions = db.query(func.count(Question.id))\
                        .filter(Question.quiz_id == quiz_id)\
                        .scalar()

    # 3) 문제 조회 (OFFSET + LIMIT)
    questions = (
        db.query(Question)
        .filter(Question.quiz_id == quiz_id)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    # 4) 관리자 랜덤 설정이 있으면 적용
    if quiz.is_random_questions:
        random.shuffle(questions)

    questions_data = []
    for question in questions:
        choices = db.query(Choice).filter(Choice.question_id == question.id).all()
        
        if quiz.is_random_choices:
            random.shuffle(choices)

        question_response = UserQuestionResponse(
            id=question.id,
            question_text=question.question_text,
            choices=[UserChoiceResponse(id=choice.id, choice_text=choice.choice_text) for choice in choices]
        )
        questions_data.append(question_response)

    # 5) total_pages 계산
    total_pages = (total_questions + page_size - 1) // page_size

    return UserQuizDetailResponse(
        id=quiz.id,
        title=quiz.title,
        description=quiz.description,
        questions=questions_data,
        current_page=page,
        total_pages=total_pages
    )

def update_quiz_settings(
    db: Session, quiz_id: int, settings: UpdateQuizSettingsRequest
) -> UpdateQuizSettingsResponse:
    """관리자가 퀴즈의 랜덤 설정 & 페이지당 문항수 등을 변경"""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="해당 퀴즈를 찾을 수 없습니다.")

    if settings.is_random_questions is not None:
        quiz.is_random_questions = settings.is_random_questions

    if settings.is_random_choices is not None:
        quiz.is_random_choices = settings.is_random_choices

    if settings.questions_per_page is not None:
        if settings.questions_per_page < 1:
            raise HTTPException(status_code=400, detail="페이지당 문항 수는 1 이상이어야 합니다.")
        quiz.questions_per_page = settings.questions_per_page

    db.commit()
    db.refresh(quiz)

    return UpdateQuizSettingsResponse(
        id=quiz.id,
        title=quiz.title,
        is_random_questions=quiz.is_random_questions,
        is_random_choices=quiz.is_random_choices,
        questions_per_page=quiz.questions_per_page
    )

def create_quiz_record(db: Session, quiz_id: int, user_id: int) -> QuizRecord:
    """새로운 응시 기록 생성"""
    record = QuizRecord(
        quiz_id=quiz_id,
        user_id=user_id,
        score=0
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

def get_quiz_record_by_id(db: Session, record_id: int) -> QuizRecord:
    """응시 기록 조회"""
    return db.query(QuizRecord).filter(QuizRecord.id == record_id).first()

def submit_answers(db: Session, record: QuizRecord, answers: SubmitAnswersRequest) -> QuizRecord:
    """답안 제출 -> 자동 채점 -> quiz_record 업데이트 (100점 만점 기준)"""

    total_questions = db.query(Question).filter(Question.quiz_id == record.quiz_id).count()  
    correct_answers = 0  

    for ans in answers.answers:
        choice = db.query(Choice).filter(Choice.id == ans.choice_id, Choice.question_id == ans.question_id).first()
        if not choice:
            raise HTTPException(status_code=400, detail=f"잘못된 선택지: choice_id={ans.choice_id} (question_id={ans.question_id}에 속하지 않음)")

        new_answer = Answer(
            quiz_record_id=record.id,
            question_id=ans.question_id,
            choice_id=ans.choice_id
        )
        db.add(new_answer)

        if choice.is_correct:
            correct_answers += 1

    record.score = round((correct_answers / total_questions) * 100, 2) if total_questions > 0 else 0

    db.commit()
    db.refresh(record)
    return record


def get_user_quiz_list(db: Session, user_id: int, completed: bool) -> List[UserQuizListResponse]:
    """
    completed=true  -> 사용자가 이미 응시한 시험 목록 (quiz_record 존재)
    completed=false -> 사용자가 응시하지 않은 시험 목록 (quiz_record 없음)
    """
    if completed:
        # 응시한 시험 목록
        # SELECT q.*, r.score 
        # FROM quiz_record r
        # JOIN quiz q ON r.quiz_id = q.id
        # WHERE r.user_id = :user_id
        rows = db.query(
            Quiz.id.label("quiz_id"),
            Quiz.title.label("quiz_title"),
            Quiz.description.label("quiz_desc"),
            QuizRecord.score.label("quiz_score")
        )\
        .join(QuizRecord, QuizRecord.quiz_id == Quiz.id)\
        .filter(QuizRecord.user_id == user_id)\
        .all()

        result = []
        for row in rows:
            result.append(
                UserQuizListResponse(
                    id=row.quiz_id,
                    title=row.quiz_title,
                    description=row.quiz_desc,
                    score=row.quiz_score  # 응시한 시험이므로 점수 표시
                )
            )
        return result

    else:
        # 응시하지 않은 시험 목록
        # SELECT q.* 
        # FROM quiz q
        # LEFT JOIN quiz_record r 
        #   ON (q.id = r.quiz_id AND r.user_id = :user_id)
        # WHERE r.id IS NULL
        subq = db.query(Quiz.id)\
            .join(QuizRecord, QuizRecord.quiz_id == Quiz.id)\
            .filter(QuizRecord.user_id == user_id)\
            .subquery()

        # quiz.id NOT IN (subquery)
        rows = db.query(Quiz)\
            .filter(~Quiz.id.in_(subq))
            # or .filter(Quiz.id.notin_(subq)) 
        quizzes = rows.all()
        
        # 응시 안 한 시험 목록이므로 score=None
        result = []
        for q in quizzes:
            result.append(
                UserQuizListResponse(
                    id=q.id,
                    title=q.title,
                    description=q.description,
                    score=None
                )
            )
        return result
