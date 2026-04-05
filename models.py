from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    chats = relationship("ChatHistory", back_populates="user")

class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    password = Column(String(50))

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
    user_id = Column(Integer, ForeignKey('users.id'))
    role = Column(String(20), nullable=False) # 'user' or 'assistant'
    message = Column(Text, nullable=False)
    model_name = Column(String(50))
    timestamp = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="chats")

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
