
from fastapi import APIRouter

router = APIRouter()

@router.get("/test")
def test_route():
    return {"message": "This is a test route from router ✅"}
