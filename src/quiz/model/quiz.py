from common.db.database import Base
from sqlalchemy import TIMESTAMP, Column, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import Boolean


class Quiz(Base):
    __tablename__ = "quiz"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)  # 퀴즈 제목
    description = Column(Text)  # 퀴즈 설명
    is_random_questions = Column(Boolean, default=False)
    is_random_choices = Column(Boolean, default=False)
    questions_per_page = Column(Integer, default=10)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    questions = relationship("Question", back_populates="quiz")
