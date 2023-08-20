from keycloak.exceptions import KeycloakError
from fastapi import APIRouter, Depends, HTTPException, status, Query

from src.auth.dependencies import RoleChecker, get_admin_service
from src.auth.service import KeycloakAdminService
from src.admin.schemas import AssignRoleDto

router = APIRouter()
allow_admin = RoleChecker(["realm:admin"])


def get_admin(admin_service: KeycloakAdminService = Depends(get_admin_service)):
    try:
        return admin_service.get_admin_client()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to connect to Admin API: {e}",
        )


@router.post("/assign-role", dependencies=[Depends(allow_admin)])
def assign_role(data: AssignRoleDto, admin=Depends(get_admin)):
    try:
        user_id = admin.get_user_id(data.username)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        role_name = data.roleName
        if role_name.startswith("realm:"):
            role_name = role_name.replace("realm:", "")

        # Get role representation
        role = admin.get_realm_role(role_name)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
            )

        admin.assign_realm_roles(user_id=user_id, roles=[role])
        return {"message": f"Role {role_name} assigned to user {data.username}"}

    except KeycloakError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        # print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/users/search", dependencies=[Depends(allow_admin)])
def search_users(
    username: str = Query(None),  # Make username optional for role-based search
    role_name: str = Query(None),  # New optional role_name parameter
    admin=Depends(get_admin),
):
    try:
        # Start with a query based on username if provided
        query_params = {}
        if username:
            query_params["username"] = username

        # Get users from Keycloak.
        keycloak_users = admin.get_users(query_params)

        filtered_users = []
        if role_name:
            clean_role_name = role_name.replace("realm:", "")  # Clean prefix if present
            for user in keycloak_users:
                realm_access = user.get("realm_access", {})
                roles = realm_access.get("roles", [])
                if clean_role_name in roles:
                    filtered_users.append(user)
            return filtered_users
        else:
            # If no role_name is provided, return users found by username or all users
            return keycloak_users

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
