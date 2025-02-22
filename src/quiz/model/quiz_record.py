from common.db.database import Base
from sqlalchemy import Boolean, Column, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import TIMESTAMP


class QuizRecord(Base):
    __tablename__ = "quiz_record"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quiz.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, nullable=False)  # 사용자 식별
    score = Column(Integer, default=0)         # 최종 점수
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    answers = relationship("Answer", back_populates="quiz_record")
