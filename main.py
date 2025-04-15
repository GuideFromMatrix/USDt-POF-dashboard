
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# Initialize the FastAPI app
app = FastAPI()

# Add CORS middleware to allow frontend to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Pydantic model for user data validation
class User(BaseModel):
    email: str
    password: str

# In-memory user storage (Replace with your real database in production)
users = []

# POST endpoint for user signup
@app.post("/signup")
async def signup(user: User):
    # Check if the email already exists
    if any(u['email'] == user.email for u in users):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Save the user to the in-memory list
    users.append({"email": user.email, "password": user.password})
    return {"message": "Signup successful"}
