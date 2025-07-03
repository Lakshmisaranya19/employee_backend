# interacts with DB (logic)
from sqlalchemy.orm import Session
from app.models.users import User

def login_user(db: Session, email: str, password: str):
    return db.query(User).filter(User.email == email, User.hashed_password == password).first()
