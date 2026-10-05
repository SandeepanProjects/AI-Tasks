from fastapi import Header
from .models import Principal

def get_principal(
    x_user_id: str = Header(default="demo-user"),
    x_tenant_id: str = Header(default="demo-tenant"),
    x_roles: str = Header(default="advisor"),
) -> Principal:
    return Principal(
        subject=x_user_id,
        tenant_id=x_tenant_id,
        roles=frozenset(x_roles.split(",")),
    )
