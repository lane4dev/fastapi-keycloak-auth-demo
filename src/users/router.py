from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status

from src.auth.dependencies import get_current_user, RoleChecker

router = APIRouter()
allow_admin = RoleChecker(["realm:admin"])


class UpdateBioDto(BaseModel):
    userId: str
    bio: str


@router.get("/me")
def me(user_info: dict = Depends(get_current_user)):
    return user_info


@router.post("/update-bio")
def update_bio(data: UpdateBioDto, user_info: dict = Depends(get_current_user)):
    user_id = user_info.get("sub")
    if data.userId != user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can only update your own bio",
        )

    return {
        "message": "Bio updated successfully",
        "userId": data.userId,
        "newBio": data.bio,
    }


@router.get("/admin-debug", dependencies=[Depends(allow_admin)])
def admin_debug(user_info: dict = Depends(get_current_user)):
    return {"debugInfo": "This is secret admin info", "user": user_info}
