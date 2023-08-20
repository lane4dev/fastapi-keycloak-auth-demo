from fastapi import Depends, APIRouter
from fastapi.security import HTTPBearer

from src.auth.dependencies import get_current_user

from src.auth.router import router as auth_router
from src.developer.router import router as developer_router
from src.manager.router import router as manager_router
from src.resource.router import router as resource_router
from src.users.router import router as user_router
from src.admin.router import router as admin_router

token_auth_scheme = HTTPBearer()

router = APIRouter()

@router.get("/health", tags=["default"])
async def index():
    """
    Index route.

    Returns:
        Dict
    """
    return {"status": "ok"}
