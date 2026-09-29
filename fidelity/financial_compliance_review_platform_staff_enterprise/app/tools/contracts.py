from dataclasses import dataclass
from typing import Callable, Awaitable, Any

@dataclass(frozen=True)
class ToolContract:
    name: str
    permission: str
    side_effect: str
    timeout_seconds: float
    audit_action: str

# Registry is explicit: adding a tool requires code review and a declared capability.
TOOL_REGISTRY = {
    "policy_search": ToolContract(
        name="policy_search", permission="policy:read", side_effect="read_only",
        timeout_seconds=8.0, audit_action="policy_search",
    ),
}

def assert_tool_allowed(name: str, granted_permissions: set[str]) -> ToolContract:
    contract = TOOL_REGISTRY.get(name)
    if contract is None:
        raise PermissionError("Tool is not allowlisted")
    if contract.permission not in granted_permissions:
        raise PermissionError("Principal lacks tool permission")
    return contract
