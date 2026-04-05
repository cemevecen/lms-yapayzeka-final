import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from models import Base, User, Course, ChatHistory

load_dotenv()

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./lms.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)

# CRUD Operations Helper
def add_chat_message(db, role, message, model_name, user_id=None):
    new_msg = ChatHistory(role=role, message=message, model_name=model_name, user_id=user_id)
    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)
    return new_msg

def get_chat_history(db, limit=20):
    return db.query(ChatHistory).order_by(ChatHistory.timestamp.asc()).limit(limit).all()

def add_sample_course(db, title, description, content):
    course = Course(title=title, description=description, content=content)
    db.add(course)
    db.commit()
    db.refresh(course)
    return course

def get_all_courses(db):
    return db.query(Course).all()

def delete_course(db, course_id):
    course = db.query(Course).filter(Course.id == course_id).first()
    if course:
        db.delete(course)
        db.commit()
        return True
    return False
