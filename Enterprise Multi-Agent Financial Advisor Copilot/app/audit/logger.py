import json
import datetime


class AuditLogger:

    @staticmethod
    def log(
        user_id,
        action,
        data
    ):

        log_entry = {

            "timestamp":
            str(datetime.datetime.utcnow()),

            "user_id": user_id,

            "action": action,

            "data": data
        }

        print(
            json.dumps(log_entry)
        )