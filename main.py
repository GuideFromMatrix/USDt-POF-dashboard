
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

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

# In-memory "fake" user storage
users = []

# Optional root route (for 404 testing)
@app.get("/")
async def root():
    return {"message": "Backend is running, bruda 😎"}

# POST /signup
@app.post("/signup")
async def signup(user: User):
    if any(u["email"] == user.email for u in users):
        raise HTTPException(status_code=400, detail="Email already registered")
    users.append({"email": user.email, "password": user.password})
    return {"message": "Signup successful"}

# POST /login
@app.post("/login")
async def login(user: User):
    for u in users:
        if u["email"] == user.email and u["password"] == user.password:
            return {"message": "Login successful", "token": "mocked-jwt-token"}
    raise HTTPException(status_code=401, detail="Invalid credentials")
