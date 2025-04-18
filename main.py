
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import base64
import json

# Initialize the FastAPI app
app = FastAPI()

# Allow frontend CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for signup/login
class User(BaseModel):
    email: str
    password: str

# In-memory "fake" user storage with wallet-related fields
users = []

def get_user(email: str):
    for user in users:
        if user["email"] == email:
            return user
    return None

# Optional root route (for 404 testing)
@app.get("/")
async def root():
    return {"message": "Backend is running, bruda 😎"}

# POST /signup
@app.post("/signup")
async def signup(user: User):
    if any(u["email"] == user.email for u in users):
        raise HTTPException(status_code=400, detail="Email already registered")
    users.append({
        "email": user.email,
        "password": user.password,
        "wallet": None,
        "wallet_history": [],
        "internal_balance": 0
    })
    return {"message": "Signup successful"}

# POST /login
@app.post("/login")
async def login(user: User):
    for u in users:
        if u["email"] == user.email and u["password"] == user.password:
            # Create a base64-encoded payload with email
            payload = {"email": user.email}
            encoded_payload = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
            # Return a mock token (fake header.payload.signature)
            token = f"header.{encoded_payload}.signature"
            return {"message": "Login successful", "token": token}
    raise HTTPException(status_code=401, detail="Invalid credentials")
