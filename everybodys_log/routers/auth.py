
from ..models.google_login import GoogleLoginRequest
from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", status_code=status.HTTP_200_OK)
async def login(user: GoogleLoginRequest) -> dict:
    if not user:
        raise HTTPException(status_code=401, detail="Authentication failed, recieved no user data.")   

    return {"message": f"User {user.name} logged in successfully."}