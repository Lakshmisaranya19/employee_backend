#  validates input via Pydantic
from pydantic import BaseModel

class UserLogin(BaseModel):
    email: str
    password: str
