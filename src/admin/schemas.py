from pydantic import BaseModel


class AssignRoleDto(BaseModel):
    username: str
    roleName: str
