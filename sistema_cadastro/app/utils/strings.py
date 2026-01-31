import re

def only_digits (text: str) -> str:
    return re.sub (r"\D", "", text or "") # somente aspas duplas