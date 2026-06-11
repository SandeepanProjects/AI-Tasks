class AuditEvent:

    def __init__(
        self,
        user_id,
        action,
        payload
    ):

        self.user_id = user_id

        self.action = action

        self.payload = payload