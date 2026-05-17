class ConversationMemory:
    def __init__(self):
        self.history = []

    def add_message(
        self,
        role,
        content,
    ):
        self.history.append(
            {
                "role": role,
                "content": content,
            }
        )

    def get_messages(self):
        return self.history[-20:]