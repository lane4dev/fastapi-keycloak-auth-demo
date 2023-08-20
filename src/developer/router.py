from fastapi import APIRouter, Depends, Body

from src.auth.dependencies import RoleChecker


router = APIRouter()

allow_admin = RoleChecker(["realm:admin"])
allow_developer = RoleChecker(["realm:developer"])
allow_developer_or_admin = RoleChecker(["realm:developer", "realm:admin"])


@router.post("/")
def create(developer: dict = Body(...), _=Depends(allow_developer_or_admin)):
    return {"message": "This action adds a new developer;"}


@router.get("/")
def find_all():
    return {"message": "This action returns all developer;"}


@router.get("/{id}")
def find_one(id: int):
    return {"message": f"This action returns a #{id} developer;"}


@router.patch("/{id}")
def update(id: int, developer: dict = Body(...), _=Depends(allow_developer)):
    return {"message": f"This action updates a #{id} developer;"}


@router.delete("/{id}")
def delete(id: int, _=Depends(allow_admin)):
    return {"message": f"This action deletes a #{id} developer;"}
