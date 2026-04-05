from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Course(Base):
    __tablename__ = 'courses'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class ChatHistory(Base):
    __tablename__ = 'chat_histories'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    role = Column(String(20), nullable=False) # 'user' or 'assistant'
    message = Column(Text, nullable=False)
    model_name = Column(String(50))
    timestamp = Column(DateTime, default=datetime.utcnow)

class QuizResult(Base):
    __tablename__ = 'quiz_results'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    quiz_title = Column(String(200))
    student_name = Column(String(100))
    score = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db(engine):
    Base.metadata.create_all(engine)
