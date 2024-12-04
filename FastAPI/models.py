# models.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from typing import List
from typing import Union

class User(BaseModel):
    name: str = Field(..., min_length=1)  # name must have a minimum length of 1
    email: EmailStr
    password: str

class Login(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: EmailStr

class CommandRequest(BaseModel):
    commands: List[str]

class EmailModel(BaseModel):
    addresses: List[str]