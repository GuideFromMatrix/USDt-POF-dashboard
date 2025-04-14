from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import router
import uvicorn
import os

app = FastAPI()

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include your API router
app.include_router(router)

# Optional test route for checking server is alive
@app.get("/")
def read_root():
    return {"status": "Server is live!"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Use Render's port if available
    uvicorn.run(app, host="0.0.0.0", port=port)