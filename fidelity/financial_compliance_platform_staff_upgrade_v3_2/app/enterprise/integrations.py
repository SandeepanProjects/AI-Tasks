"""Least-privilege connector contracts and allowlisted HTTP adapter."""
from dataclasses import dataclass
from typing import Protocol, Any
from urllib.parse import urlparse
import httpx

@dataclass(frozen=True)
class ToolContext:
    tenant_id: str
    subject_id: str
    permissions: frozenset[str]

class ReadOnlyConnector(Protocol):
    name: str
    required_permission: str
    async def fetch(self, resource_id: str, context: ToolContext) -> dict[str, Any]: ...

class AllowlistedHttpConnector:
    def __init__(self, name: str, base_url: str, allowed_hosts: set[str], required_permission: str,
                 timeout_seconds: float = 5.0):
        host = urlparse(base_url).hostname
        if not host or host not in allowed_hosts or urlparse(base_url).scheme != "https":
            raise ValueError("connector URL must be HTTPS and explicitly allowlisted")
        self.name, self.base_url, self.required_permission = name, base_url.rstrip("/"), required_permission
        self.timeout_seconds = timeout_seconds
    async def fetch(self, resource_id: str, context: ToolContext) -> dict:
        if self.required_permission not in context.permissions:
            raise PermissionError("connector permission denied")
        if not resource_id or "/" in resource_id or ".." in resource_id:
            raise ValueError("invalid resource identifier")
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.get(f"{self.base_url}/{resource_id}", headers={"X-Tenant-Context": context.tenant_id})
            response.raise_for_status()
            return response.json()
