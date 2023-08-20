from fastapi import Depends, APIRouter
from fastapi.security import HTTPBearer

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


router.include_router(
    auth_router,
    prefix="/auth",
    tags=["auth"],
)

router.include_router(
    developer_router,
    prefix="/developer",
    tags=["developer"],
    # Removed global dependency to allow public routes
)

router.include_router(
    manager_router,
    prefix="/manager",
    tags=["manager"],
    # Manager router internally handles permissions, but we can also add it here if we want strict module level
    # Keeping it internal is fine.
)

router.include_router(
    resource_router,
    prefix="/resource",
    tags=["resource"],
    dependencies=[Depends(token_auth_scheme)], # Resource routes need at least a valid token
)

router.include_router(
    user_router,
    prefix="/user",
    tags=["user"],
    dependencies=[Depends(token_auth_scheme)], # User routes need at least a valid token
)

router.include_router(
    admin_router,
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(token_auth_scheme)], # Admin routes need token (and role check inside)
)
