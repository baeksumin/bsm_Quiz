from common.db.database import Base
from sqlalchemy import TIMESTAMP, Boolean, Column, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class Answer(Base):
    __tablename__ = "answer"

    id = Column(Integer, primary_key=True, index=True)
    quiz_record_id = Column(Integer, ForeignKey("quiz_record.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("question.id", ondelete="CASCADE"), nullable=False)
    choice_id = Column(Integer, ForeignKey("choice.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # 역방향 관계
    quiz_record = relationship("QuizRecord", back_populates="answers")
