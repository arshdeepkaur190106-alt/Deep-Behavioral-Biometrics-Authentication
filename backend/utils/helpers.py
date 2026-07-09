from typing import Optional
from fastapi import Request


def get_client_ip(request: Request) -> Optional[str]:
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    if request.client:
        return request.client.host

    return None


def get_device_info(request: Request) -> Optional[str]:
    return request.headers.get("User-Agent")


def serialize_object_id(value) -> str:
    return str(value)