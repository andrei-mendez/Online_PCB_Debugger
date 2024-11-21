# database.py
from motor.motor_asyncio import AsyncIOMotorClient
from models import User
from passlib.context import CryptContext
from fastapi import HTTPException

# MongoDB URI and Database Connection Setup
mongodb_uri = 'mongodb://localhost:27017/DebuggerData'
client = AsyncIOMotorClient(mongodb_uri)
database = client["DebuggerData"]
users = database["Users"]

# Password hashing setup
pwd_cxt = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hashing functions
class Hash:
    @staticmethod
    def bcrypt(password: str) -> str:
        return pwd_cxt.hash(password)
    
    @staticmethod
    def verify(hashed: str, plain: str) -> bool:
        return pwd_cxt.verify(plain, hashed)

# Database operations
async def create_user(user: User):
    # Check if email is already registered
    existing_user = await users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash the password
    hashed_pass = Hash.bcrypt(user.password)

    # Insert user into the database
    user_data = user.dict()  # Convert to dictionary and add hashed password
    user_data["password"] = hashed_pass
    result = await users.insert_one(user_data)
    if result.inserted_id:
        return {"res": "created"}
    else:
        raise HTTPException(status_code=500, detail="User registration failed")

async def find_user_by_email(email: str):
    return await users.find_one({"email": email})
