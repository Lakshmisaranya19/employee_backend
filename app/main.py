# from fastapi import FastAPI, Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from sqlalchemy.orm import Session
# from app.db import get_db, engine
# from app.schemas.user import UserCreate, UserResponse, Token
# from app.crud import user as crud_user
from sqlalchemy import func
from app.models import users as user_model
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from app.db import get_db
from app.models.users import User
from app.models.password_reset import PasswordReset
from app.utils.security import get_password_hash
import os
import requests
import certifi
# from app.utils.security import create_access_token, verify_token
# from app.config import ACCESS_TOKEN_EXPIRE_MINUTES
# # Add to top of main.py
# from datetime import datetime, timedelta
# import random, string
# import smtplib
# from email.mime.text import MIMEText
# from app.models.password_reset import PasswordReset  # You’ll create this model
# from app.models.users import User
# from app.utils.security import get_password_hash
# from app.models.password_reset import PasswordReset
# from app.utils.email_sender import send_otp_email
# from sendgrid import SendGridAPIClient
# from sendgrid.helpers.mail import Mail
# import os
# from dotenv import load_dotenv
# import certifi
# os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
# from sendgrid import SendGridAPIClient
# from sendgrid.helpers.mail import Mail
# load_dotenv()
# refresh-token
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db import get_db, engine
from app.config import ACCESS_TOKEN_EXPIRE_MINUTES
from app.schemas.user import UserCreate, UserResponse, Token
from app.crud import user as crud_user
from app.models.users import User
from app.models.password_reset import PasswordReset
from app.utils.security import (
    create_access_token, verify_token,
    get_password_hash
)
import os, random, string
from datetime import datetime, timedelta,timezone
import requests, certifi

PasswordReset.metadata.create_all(bind=engine)
app = FastAPI(title="Employee Backend", version="1.0.0")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
# Create DB tables
user_model.Base.metadata.create_all(bind=engine)
# Dependency to extract user from token
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    email = verify_token(token)
    if email is None:
        raise HTTPException(status_code=401, detail="Invalid token", headers={"WWW-Authenticate": "Bearer"})
    user = crud_user.get_user_by_email(db, email=email)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@app.get("/")
def root():
    return {"message": "Employee Backend API is running!"}

@app.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = crud_user.create_user(db, user.email, user.password)
    if db_user is None:
        raise HTTPException(status_code=400, detail="Email already registered")
    return db_user

@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud_user.login_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user.email}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=UserResponse)
def read_users_me(current_user: user_model.User = Depends(get_current_user)):
    return current_user

@app.get("/protected")
def protected_route(current_user: user_model.User = Depends(get_current_user)):
    return {"message": f"Hello {current_user.email}, this is a protected route!"}

@app.post("/forgot-password")
def forgot_password(email: str, db: Session = Depends(get_db)):
    otp = ''.join(random.choices(string.digits, k=6))
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)

    # Store OTP
    reset = PasswordReset(email=email, otp=otp, expires_at=expires_at)
    db.add(reset)
    db.commit()

    # Email body (funny)
    subject = "🕵️ OTP Incoming – Top Secret!"
    body = f"""
    Hello Agent,

    We heard your memory slipped. Here's your one-time password to reset it all:

    👉 OTP: {otp}

    Use it within 5 minutes or risk the wrath of the self-destructing bunny 🐰💥

    Stay safe,
    Password Intelligence Unit
    """
    # send_otp_email(email, otp)/
    send_email(subject, body, email)
    return {"message": "OTP sent! Check your inbox, Agent 🕶️(If not in inbox 📧 ,check your spam ⚠️)"}

@app.post("/verify-otp")
def verify_otp(email: str, otp: str, db: Session = Depends(get_db)):
    reset = db.query(PasswordReset).filter(
        PasswordReset.email == email,
        PasswordReset.otp == otp,
        PasswordReset.is_used == False,
        PasswordReset.expires_at > datetime.now(timezone.utc)
    ).first()

    if not reset:
        raise HTTPException(status_code=400, detail="OTP expired or incorrect 😬")

    return {"message": "OTP verified! You can now reset your password 🛠️"}

@app.post("/reset-password")
def reset_password(email: str, otp: str, new_password: str, db: Session = Depends(get_db)):
    # Normalize the email input
    email = email.strip().lower()

    # ✅ Debug: Show what we received
    print("📩 Sanitized Email:", repr(email))
    print("🔑 OTP:", otp)

    # ✅ Check if OTP is valid, not used, and not expired
    reset = db.query(PasswordReset).filter(
        func.lower(PasswordReset.email) == email,
        PasswordReset.otp == otp,
        PasswordReset.is_used == False,
        PasswordReset.expires_at > datetime.now(timezone.utc)
    ).first()

    print("📬 OTP record found:", reset is not None)

    if not reset:
        raise HTTPException(status_code=400, detail="OTP expired or invalid")

    # ✅ Optional: Debug all emails in DB
    users = db.query(User).all()
    print("🧾 Users in DB:")
    for u in users:
        print("->", repr(u.email))

    # ✅ Fetch user case-insensitively
    user = db.query(User).filter(func.lower(User.email) == email).first()

    print("👤 User found:", user is not None)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # ✅ Update the password
    user.hashed_password = get_password_hash(new_password)

    # ✅ Mark OTP as used
    reset.is_used = True

    # ✅ Commit both changes
    db.commit()

    return {"message": "✅ Password reset successfully! Try not to forget it again 😅"}

def send_email(subject: str, body: str, to_email: str):
    api_key = os.getenv("SENDGRID_API_KEY")
    from_email = os.getenv("FROM_EMAIL")

    if not api_key or not from_email:
        raise ValueError("Missing SENDGRID_API_KEY or FROM_EMAIL in environment variables")

    data = {
        "personalizations": [{
            "to": [{"email": to_email}],
            "subject": subject
        }],
        "from": {"email": from_email},
        "content": [{
            "type": "text/plain",
            "value": body
        }]
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            "https://api.sendgrid.com/v3/mail/send",
            headers=headers,
            json=data,
            verify=certifi.where()
        )
        print("SendGrid Status:", response.status_code)
        if response.status_code >= 400:
            print("SendGrid Error:", response.text)
    except Exception as e:
        print("Email send error:", str(e))
