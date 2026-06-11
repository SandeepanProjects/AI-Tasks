ROLE_ADMIN = "admin"

ROLE_ANALYST = "analyst"

ROLE_VIEWER = "viewer"


PERMISSIONS = {

    ROLE_ADMIN: [
        "chat",
        "upload",
        "delete"
    ],

    ROLE_ANALYST: [
        "chat",
        "upload"
    ],

    ROLE_VIEWER: [
        "chat"
    ]
}