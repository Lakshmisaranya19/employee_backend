# connects everything , gives API endpoint, connects to DB, checks the logic, and returns a response
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db, engine
from app.schemas.user import UserLogin
from app.crud import user as crud_user
from app.models import users as user

app = FastAPI()

# This will create the 'users' table if it doesn’t exist
user.Base.metadata.create_all(bind=engine)

@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    print("Login API called")
    authenticated_user = crud_user.login_user(db, user.email, user.password)
    print("User lookup done")
    if not authenticated_user:
        print("Invalid login")
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"message": "Login successful"}
