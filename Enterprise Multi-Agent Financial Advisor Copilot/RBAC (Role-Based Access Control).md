RBAC is actually one of the most important enterprise features in your Financial Advisor Copilot.

Many junior AI projects have:

```text
User
  ↓
Ask Question
  ↓
Get Answer
```

But real companies like Fidelity, JPMorgan, Goldman Sachs, Morgan Stanley, etc. cannot work this way.

Different people should have different permissions.

That's why we use **RBAC (Role-Based Access Control).**

---

# What is RBAC?

RBAC means:

```text
Role
    ↓
Determines
    ↓
What user can access
```

Instead of:

```text
User A → Allow
User B → Deny
User C → Allow
```

we assign roles.

Example:

```text
Admin
Advisor
Compliance Officer
Analyst
Viewer
```

---

# Why Is RBAC Needed?

Imagine your company has:

```text
Financial Advisor
Compliance Team
Admin Team
Clients
```

Should everyone be able to:

```text
Upload Documents?
Delete Documents?
View Audit Logs?
Access Client Data?
```

No.

---

# Example

### Admin

Can:

```text
Manage Users
Upload Documents
Delete Documents
View Logs
Manage Models
```

---

### Advisor

Can:

```text
Ask Questions
Generate Reports
View Client Portfolios
```

Cannot:

```text
Delete Documents
Manage Users
```

---

### Compliance Officer

Can:

```text
Review Recommendations
View Audit Logs
Access Compliance Reports
```

Cannot:

```text
Delete Users
```

---

### Client

Can:

```text
View Own Reports
Ask Questions
```

Cannot:

```text
View Other Client Data
```

---

# Where RBAC Sits in Architecture

```text
User
  ↓
JWT Authentication
  ↓
RBAC Check
  ↓
API Endpoint
  ↓
Business Logic
```

---

# Flow Example

User:

```text
John
Role = Advisor
```

tries:

```http
DELETE /documents/123
```

---

Request reaches:

```text
api/documents.py
```

---

RBAC Middleware checks:

```python
user.role
```

Result:

```python
"advisor"
```

---

Policy says:

```python
DELETE_DOCUMENT
```

allowed only for:

```python
admin
```

---

System returns:

```json
{
  "error": "Permission Denied"
}
```

---

# Typical RBAC Folder

Usually:

```text
app/auth/
│
├── jwt.py
├── dependencies.py
├── permissions.py
└── roles.py
```

---

# roles.py

Defines roles.

Example:

```python
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    ADVISOR = "advisor"
    COMPLIANCE = "compliance"
    CLIENT = "client"
```

---

# permissions.py

Defines what each role can do.

Example:

```python
ROLE_PERMISSIONS = {
    "admin": [
        "upload_docs",
        "delete_docs",
        "manage_users"
    ],

    "advisor": [
        "ask_questions",
        "generate_reports"
    ],

    "client": [
        "view_reports"
    ]
}
```

---

# JWT + RBAC

When user logs in:

```python
token = {
    "user_id": 123,
    "role": "advisor"
}
```

stored inside JWT.

---

Later:

```http
Authorization: Bearer eyJ...
```

---

JWT Service extracts:

```python
{
   "user_id":123,
   "role":"advisor"
}
```

---

RBAC uses that role.

---

# Example Dependency

FastAPI commonly uses:

```python
def require_role(required_roles):
```

Example:

```python
@router.delete("/documents")
async def delete_document(
    user=Depends(
        require_role(["admin"])
    )
):
```

---

What Happens?

If role:

```python
admin
```

Access granted.

---

If role:

```python
advisor
```

Access denied.

---

# Database Side

PostgreSQL usually contains:

```sql
users
```

| id | email                                             | role    |
| -- | ------------------------------------------------- | ------- |
| 1  | [admin@company.com](mailto:admin@company.com)     | admin   |
| 2  | [advisor@company.com](mailto:advisor@company.com) | advisor |
| 3  | [client@company.com](mailto:client@company.com)   | client  |

---

During login:

```python
SELECT role
FROM users
WHERE email = ?
```

Role loaded.

---

JWT generated:

```python
{
   "role":"advisor"
}
```

---

RBAC uses this value.

---

# In Your Financial Advisor Copilot

RBAC protects:

### Document Upload

```text
Only Admin
```

---

### User Management

```text
Only Admin
```

---

### Audit Logs

```text
Admin
Compliance
```

---

### Financial Recommendations

```text
Advisor
Client
```

---

### Evaluation Dashboard

```text
Admin
ML Engineer
```

---

# Real Fidelity-Style Example

Suppose:

```text
User = Advisor
```

asks:

```text
Generate retirement plan
```

RBAC:

```text
Allowed
```

---

Same user tries:

```text
Delete investment policy documents
```

RBAC:

```text
Denied
```

---

Admin tries:

```text
Delete investment policy documents
```

RBAC:

```text
Allowed
```

---

# Interview Answer

If asked:

### Why did you implement RBAC?

You can answer:

> "RBAC was implemented to enforce role-based access control across the platform. Different user types such as advisors, compliance officers, administrators, and clients have different permissions. JWT tokens carry role information, and FastAPI dependencies enforce authorization policies before business logic is executed. This ensures security, regulatory compliance, and data isolation in a multi-user financial environment."

That's the explanation a Senior/Staff AI Engineer would typically give in a design review or architecture interview.
