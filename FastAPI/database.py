# database.py
from motor.motor_asyncio import AsyncIOMotorClient
from models import User
from passlib.context import CryptContext
from fastapi import HTTPException
from fastapi import BackgroundTasks
from utils import create_url_safe_token
from mail import mail, create_message


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
async def create_user(user: User, bg_tasks: BackgroundTasks):
    # Check if email is already registered
    existing_user = await users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash the password
    hashed_pass = Hash.bcrypt(user.password)

    # Create the user data
    user_data = user.dict()
    user_data["password"] = hashed_pass
    user_data["is_verified"] = False  # Add a field to mark the email as unverified initially

    # Insert user into the database
    result = await users.insert_one(user_data)
    if result.inserted_id:
        # Generate token for email verification
        token = create_url_safe_token({"email": user.email})
        
        # Send verification email in the background
        bg_tasks.add_task(send_verification_email, user.email, token)

        return {"message": "Account created! Please check your email to verify your account."}
    else:
        raise HTTPException(status_code=500, detail="User registration failed")

async def find_user_by_email(email: str):
    return await users.find_one({"email": email})

# Background task to send the email
async def send_verification_email(user_email: str, token: str):
    verification_link = f"http://localhost:3000/verify/{token}"
    subject = "Verify Your Email"
    html_content = f"""
        <h1>Verify your Email</h1>
        <p>Please click the link below to verify your email:</p>
        <a href="{verification_link}">Verify Email</a>
    """

    emails = [user_email]
    subject = "Verify Your email"

    message = create_message(
        recipients=emails,
        subject=subject,
        body = html_content
    )

    await mail.send_message(message)

    return { "message": "Account Created! Check email to verify"}