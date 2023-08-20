from fastapi import APIRouter, Depends, Body

from src.auth.dependencies import RoleChecker

router = APIRouter()

allow_admin = RoleChecker(["realm:admin"])
allow_manager = RoleChecker(["realm:manager"])
allow_manager_or_admin = RoleChecker(["realm:manager", "realm:admin"])


@router.post("/")
def create(manager: dict = Body(...), _=Depends(allow_manager_or_admin)):
    return {"message": "This action adds a new manager;"}


@router.get("/")
def find_all(_=Depends(allow_manager)):
    return {"message": "This action returns all manager;"}


@router.get("/{id}")
def find_one(id: int, _=Depends(allow_manager)):
    return {"message": f"This action returns a #{id} manager;"}


@router.patch("/{id}")
def update(id: int, manager: dict = Body(...), _=Depends(allow_manager)):
    return {"message": f"This action updates a #{id} manager;"}


@router.delete("/{id}")
def delete(id: int, _=Depends(allow_admin)):
    return {"message": f"This action deletes a #{id} manager;"}
