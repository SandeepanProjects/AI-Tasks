import json

from app.memory.redis_client import (
    redis_client
)


class MemoryService:

    @staticmethod
    def save_message(
        user_id: str,
        role: str,
        content: str
    ):

        key = f"memory:{user_id}"

        messages = redis_client.get(key)

        if messages:
            messages = json.loads(messages)
        else:
            messages = []

        messages.append(
            {
                "role": role,
                "content": content
            }
        )

        redis_client.set(
            key,
            json.dumps(messages)
        )

    @staticmethod
    def get_memory(user_id):

        key = f"memory:{user_id}"

        data = redis_client.get(key)

        if not data:
            return []

        return json.loads(data)