import random
from datetime import datetime
from typing import List

import pytz
from fastapi.exceptions import HTTPException
from sqlalchemy import desc, func
from sqlalchemy.orm import Session
from src.quiz.model import Choice, Question, Quiz
from src.quiz.schema.schema import (ChoiceResponse, QuestionCreate,
                                    QuestionResponse, QuizCreate,
                                    QuizDetailResponse, QuizListResponse,
                                    QuizResponse)

KST = pytz.timezone("Asia/Seoul")

def check_existing_quiz(db: Session, title: str):
    """이미 존재하는 퀴즈인지 확인"""
    return db.query(Quiz).filter(Quiz.title == title).first()

def create_quiz(db: Session, quiz_data: QuizCreate):
    """퀴즈 생성 (문제 & 선택지 포함)"""
    existing_quiz = check_existing_quiz(db, quiz_data.title)
    if existing_quiz:
        raise HTTPException(status_code=409, detail="이미 동일한 제목의 퀴즈가 존재합니다.")

    new_quiz = Quiz(title=quiz_data.title, description=quiz_data.description)
    db.add(new_quiz)
    db.flush()  # quiz.id 확보

    for question_data in quiz_data.questions:
        new_question = Question(quiz_id=new_quiz.id, question_text=question_data.question_text)
        db.add(new_question)
        db.flush()  # question.id 확보

        for choice_data in question_data.choices:
            new_choice = Choice(
                question_id=new_question.id,
                choice_text=choice_data.choice_text,
                is_correct=choice_data.is_correct
            )
            db.add(new_choice)

    db.commit()
    db.refresh(new_quiz)
    return new_quiz

def get_quiz_by_id(db: Session, quiz_id: int):
    """퀴즈 ID로 퀴즈 조회"""
    return db.query(Quiz).filter(Quiz.id == quiz_id).first()

def add_questions_to_quiz(db: Session, quiz_id: int, questions: List[QuestionCreate]):
    """기존 퀴즈에 문제 추가"""
    quiz = get_quiz_by_id(db, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="해당 퀴즈를 찾을 수 없습니다.")

    for question_data in questions:
        # 문제 추가
        new_question = Question(quiz_id=quiz.id, question_text=question_data.question_text)
        db.add(new_question)
        db.flush()  # question.id 확보

        # 선택지 추가
        correct_count = sum(1 for choice in question_data.choices if choice.is_correct)
        if len(question_data.choices) < 2 or correct_count < 1:
            raise HTTPException(status_code=400, detail="각 문제는 최소 2개의 선택지를 가져야 하며, 정답이 1개 포함되어야 합니다.")

        for choice_data in question_data.choices:
            new_choice = Choice(
                question_id=new_question.id,
                choice_text=choice_data.choice_text,
                is_correct=choice_data.is_correct
            )
            db.add(new_choice)
            
    quiz.updated_at = datetime.now(KST)
    db.commit()
    return QuizResponse.from_orm(quiz)

def get_quiz_list(
    db: Session, page: int = 1, page_size: int = 10, sort_by: str = "created_at", order: str = "desc"
):
    """관리자용 퀴즈 목록 조회 (페이징 지원)"""
    sort_column = getattr(Quiz, sort_by, Quiz.created_at)
    if order == "desc":
        sort_column = desc(sort_column)

    quizzes = (
        db.query(
            Quiz.id,
            Quiz.title,
            Quiz.description,
            Quiz.created_at,
            func.count(Question.id).label("num_questions")
        )
        .outerjoin(Question, Quiz.id == Question.quiz_id)
        .group_by(Quiz.id)
        .order_by(sort_column)
        .limit(page_size)
        .offset((page - 1) * page_size)
        .all()
    )

    return [QuizListResponse.from_orm(quiz) for quiz in quizzes]

def get_quiz_detail(
    db: Session, quiz_id: int, page: int, page_size: int, sort_by: str = "created_at", order: str = "desc"
) -> QuizDetailResponse:
    """퀴즈 상세 조회 (랜덤 배치 및 페이징 지원)"""
    sort_column = getattr(Question, sort_by, Question.created_at)
    if order == "desc":
        sort_column = desc(sort_column)

    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="해당 퀴즈를 찾을 수 없습니다.")

    total_questions = db.query(func.count(Question.id)).filter(Question.quiz_id == quiz_id).scalar()

    # 퀴즈의 문제 목록 가져오기 (페이징 적용)
    questions = (
        db.query(Question)
        .filter(Question.quiz_id == quiz_id)
        .order_by(sort_column)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    questions_data = []
    for question in questions:
        choices = db.query(Choice).filter(Choice.question_id == question.id).all()

        question_response = QuestionResponse(
            id=question.id,
            question_text=question.question_text,
            choices=[ChoiceResponse.from_orm(choice) for choice in choices]
        )
        questions_data.append(question_response)

    return QuizDetailResponse(
        id=quiz.id,
        title=quiz.title,
        description=quiz.description,
        created_at=quiz.created_at,
        updated_at=quiz.updated_at,
        total_questions=total_questions,
        questions=questions_data
    )

