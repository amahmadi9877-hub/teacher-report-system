from dataclasses import dataclass


@dataclass
class ResponseError:
    status_code: str
    code: str
    message: str
