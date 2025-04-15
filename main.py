
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict

app = FastAPI()

# Enable CORS so frontend can talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dummy in-memory "database"
fake_users_db: Dict[str, str] = {}

# Models
class User(BaseModel):
    email: str
    password: str

# Signup endpoint
@app.post("/signup")
def signup(user: User):
    if user.email in fake_users_db:
        raise HTTPException(status_code=400, detail="Email already registered")
    fake_users_db[user.email] = user.password
    print(f"✅ New user signed up: {user.email}")
    return {"message": "Signup successful"}

# Login endpoint
@app.post("/login")
def login(user: User):
    if user.email not in fake_users_db or fake_users_db[user.email] != user.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    print(f"✅ User logged in: {user.email}")
    return {"token": "dummy-token-for-" + user.email}
