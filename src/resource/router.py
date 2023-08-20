from fastapi import APIRouter, Depends

from src.auth.dependencies import get_current_user


router = APIRouter()


@router.get("/dashboard")
def dashboard(user_info: dict = Depends(get_current_user)):
    realm_access = user_info.get("realm_access", {})
    roles = realm_access.get("roles", [])

    response = {
        "title": "Dashboard",
        "welcome": f"Welcome, {user_info.get('preferred_username')}!",
    }

    if "manager" in roles or "realm:manager" in roles:
        response["managerSection"] = "Manager specific content..."

    if "developer" in roles or "realm:developer" in roles:
        response["developerSection"] = "Developer specific content..."

    if "admin" in roles or "realm:admin" in roles:
        response["adminSection"] = "Admin specific content..."

    return response
