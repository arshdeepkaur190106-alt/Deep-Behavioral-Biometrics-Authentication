"""
helpers.py

General-purpose utility functions shared across backend route handlers.

Currently focused on extracting request metadata (client IP address and
device/user-agent information) from incoming FastAPI Request objects.
This metadata is used when creating AuthHistoryModel records, so that
every login attempt is logged with useful context — the same context
your teammates' behavioral biometrics model will eventually consume as
raw input features.
"""

from typing import Optional
from fastapi import Request


def get_client_ip(request: Request) -> Optional[str]:
    """
    Extracts the client's IP address from an incoming FastAPI request.

    Checks the 'X-Forwarded-For' header first, since this is the standard
    header set by reverse proxies / load balancers (common in real
    deployments, e.g. behind Nginx or a cloud load balancer). Falls back
    to the direct connection's client host if that header is absent
    (typical for local development).

    Args:
        request (Request): The incoming FastAPI request object.

    Returns:
        Optional[str]: The best-guess client IP address, or None if it
            cannot be determined.
    """
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # X-Forwarded-For can contain a comma-separated list of IPs if the
        # request passed through multiple proxies; the first entry is the
        # original client.
        return forwarded_for.split(",")[0].strip()

    if request.client:
        return request.client.host

    return None


def get_device_info(request: Request) -> Optional[str]:
    """
    Extracts the client's User-Agent string from an incoming FastAPI
    request, used as a basic device/browser identifier.

    Args:
        request (Request): The incoming FastAPI request object.

    Returns:
        Optional[str]: The raw User-Agent header string, or None if not
            provided by the client.
    """
    return request.headers.get("User-Agent")


def serialize_object_id(value) -> str:
    """
    Safely converts a MongoDB ObjectId (or any object) into its string
    representation.

    This is a small convenience wrapper used whenever raw MongoDB '_id'
    values need to be converted for inclusion in JSON API responses,
    since ObjectId is not natively JSON-serializable.

    Args:
        value: The value to convert (typically a bson.ObjectId instance).

    Returns:
        str: The string representation of the value.
    """
    return str(value)