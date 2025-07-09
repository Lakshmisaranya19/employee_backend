from sqlalchemy.orm import Session
from app.models.users import User
from app.utils.security import verify_password, get_password_hash

def login_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password) or not user.is_active:
        return None
    return user

def create_user(db: Session, email: str, password: str):
    if db.query(User).filter(User.email == email).first():
        return None
    hashed_password = get_password_hash(password)
    db_user = User(email=email, hashed_password=hashed_password, is_active=True)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()
