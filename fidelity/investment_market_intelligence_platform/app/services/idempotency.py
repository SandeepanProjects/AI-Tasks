import hashlib
import json

def request_fingerprint(tenant_id: str, payload: dict) -> str:
    canonical = json.dumps({"tenant_id": tenant_id, "payload": payload},
                           sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()
