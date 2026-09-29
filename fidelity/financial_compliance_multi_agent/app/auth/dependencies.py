from dataclasses import dataclass
from fastapi import Header, HTTPException, Depends
@dataclass
class Principal:
    subject: str; role: str; tenant_id: str="demo"
TOKENS={"demo-admin":Principal("admin-user","admin"),"demo-reviewer":Principal("reviewer-user","reviewer"),"demo-approver":Principal("approver-user","approver")}
async def current_principal(authorization: str|None=Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "): raise HTTPException(401,"Bearer token required")
    principal=TOKENS.get(authorization.removeprefix("Bearer ").strip())
    if not principal: raise HTTPException(401,"Invalid demo token")
    return principal
def require_roles(*roles):
    async def dep(principal: Principal=Depends(current_principal)):
        if principal.role not in roles: raise HTTPException(403,"Insufficient role")
        return principal
    return dep
