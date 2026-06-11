import re


EMAIL_REGEX = (
    r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
)


PHONE_REGEX = (
    r"\d{10}"
)


def contains_pii(
    text: str
):

    if re.search(
        EMAIL_REGEX,
        text
    ):
        return True

    if re.search(
        PHONE_REGEX,
        text
    ):
        return True

    return False