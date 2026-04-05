import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from models import Base, Course, ChatHistory, QuizResult
from datetime import datetime

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./lms.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

# CRUD Support
def add_chat_message(db, role, message, model_name, user_id=None):
    chat = ChatHistory(role=role, message=message, model_name=model_name, user_id=user_id)
    db.add(chat); db.commit(); return chat

def get_chat_history(db):
    return db.query(ChatHistory).order_by(ChatHistory.timestamp.asc()).all()

def add_sample_course(db, title, desc, content):
    course = Course(title=title, description=desc, content=content)
    db.add(course); db.commit(); return course

def get_all_courses(db):
    return db.query(Course).all()

def delete_course(db, course_id):
    c = db.query(Course).get(course_id)
    if c: db.delete(c); db.commit()

def add_quiz_result(db, quiz_title, student_name, score):
    res = QuizResult(quiz_title=quiz_title, student_name=student_name, score=score)
    db.add(res); db.commit(); return res

def get_quiz_results(db):
    return db.query(QuizResult).order_by(QuizResult.created_at.desc()).all()
