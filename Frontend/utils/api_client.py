"""
api_client.py

Centralized HTTP client module for the Streamlit frontend to communicate
with the FastAPI backend.

Every Streamlit page imports functions from this module instead of
calling `requests` directly and scattering raw URLs/headers throughout
the UI code. This keeps the backend's base URL, authentication header
handling, and error handling consistent and defined in exactly one place.

All functions here return a tuple of (success: bool, data_or_error).
This lets calling pages write simple, consistent handling code:

    success, result = login(username, password)
    if success:
        ... use result ...
    else:
        st.error(result)
"""

from typing import Optional, Tuple, Any, List, Dict

import requests

# ---------------------------------------------------------------------------
# Backend base URL
# ---------------------------------------------------------------------------
# In a real deployment, this should come from an environment variable
# rather than being hardcoded. For local development, FastAPI's default
# uvicorn port (8000) is used.
BASE_URL = "http://localhost:8000"

# Default timeout (in seconds) applied to every request, so the Streamlit
# app never hangs indefinitely if the backend is unreachable or slow.
DEFAULT_TIMEOUT = 10


def _build_headers(token: Optional[str] = None) -> Dict[str, str]:
    """
    Builds the standard request headers, optionally including the
    Authorization Bearer token for authenticated endpoints.

    Args:
        token (Optional[str]): The JWT access token, if the request
            requires authentication.

    Returns:
        Dict[str, str]: Header dictionary ready to pass to `requests`.
    """
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _handle_response(response: requests.Response) -> Tuple[bool, Any]:
    """
    Normalizes a requests.Response object into a consistent
    (success, data_or_error) tuple used throughout this module.

    Args:
        response (requests.Response): The raw HTTP response.

    Returns:
        Tuple[bool, Any]: (True, parsed_json) on success (2xx status),
            or (False, error_message_string) on failure.
    """
    if 200 <= response.status_code < 300:
        try:
            return True, response.json()
        except ValueError:
            # Response had no JSON body (e.g. some 204 responses).
            return True, {}

    # Attempt to extract FastAPI's standard {"detail": "..."} error format.
    try:
        error_body = response.json()
        detail = error_body.get("detail", "An unknown error occurred.")
    except ValueError:
        detail = f"Server returned status {response.status_code}."

    return False, detail


def register_user(
    username: str, email: str, full_name: str, password: str
) -> Tuple[bool, Any]:
    """
    Calls POST /auth/register to create a new user account.

    Args:
        username (str): Desired username.
        email (str): Email address.
        full_name (str): Display name.
        password (str): Plaintext password (sent over HTTPS in production;
            hashed server-side immediately upon receipt).

    Returns:
        Tuple[bool, Any]: (True, user_data) on success, or
            (False, error_message) on failure.
    """
    url = f"{BASE_URL}/auth/register"
    payload = {
        "username": username,
        "email": email,
        "full_name": full_name,
        "password": password,
    }
    try:
        response = requests.post(
            url, json=payload, headers=_build_headers(), timeout=DEFAULT_TIMEOUT
        )
        return _handle_response(response)
    except requests.exceptions.ConnectionError:
        return False, "Could not connect to the backend server. Is it running?"
    except requests.exceptions.Timeout:
        return False, "The request timed out. Please try again."


def login_user(username: str, password: str) -> Tuple[bool, Any]:
    """
    Calls POST /auth/login to authenticate a user and receive a JWT token.

    Args:
        username (str): The account's username.
        password (str): The account's plaintext password.

    Returns:
        Tuple[bool, Any]: (True, {"access_token": ..., "user": {...}}) on
            success, or (False, error_message) on failure.
    """
    url = f"{BASE_URL}/auth/login"
    payload = {"username": username, "password": password}
    try:
        response = requests.post(
            url, json=payload, headers=_build_headers(), timeout=DEFAULT_TIMEOUT
        )
        return _handle_response(response)
    except requests.exceptions.ConnectionError:
        return False, "Could not connect to the backend server. Is it running?"
    except requests.exceptions.Timeout:
        return False, "The request timed out. Please try again."


def logout_user(token: str) -> Tuple[bool, Any]:
    """
    Calls POST /auth/logout to record a logout event for the current user.

    Args:
        token (str): The current user's JWT access token.

    Returns:
        Tuple[bool, Any]: (True, confirmation_message) on success, or
            (False, error_message) on failure.
    """
    url = f"{BASE_URL}/auth/logout"
    try:
        response = requests.post(
            url, headers=_build_headers(token), timeout=DEFAULT_TIMEOUT
        )
        return _handle_response(response)
    except requests.exceptions.ConnectionError:
        return False, "Could not connect to the backend server. Is it running?"
    except requests.exceptions.Timeout:
        return False, "The request timed out. Please try again."


def get_dashboard_summary(token: str) -> Tuple[bool, Any]:
    """
    Calls GET /dashboard to retrieve the current user's aggregated
    dashboard statistics.

    Args:
        token (str): The current user's JWT access token.

    Returns:
        Tuple[bool, Any]: (True, dashboard_data) on success, or
            (False, error_message) on failure.
    """
    url = f"{BASE_URL}/dashboard"
    try:
        response = requests.get(
            url, headers=_build_headers(token), timeout=DEFAULT_TIMEOUT
        )
        return _handle_response(response)
    except requests.exceptions.ConnectionError:
        return False, "Could not connect to the backend server. Is it running?"
    except requests.exceptions.Timeout:
        return False, "The request timed out. Please try again."


def get_auth_history(
    token: str, page: int = 1, page_size: int = 10, event_type: Optional[str] = None
) -> Tuple[bool, Any]:
    """
    Calls GET /history to retrieve a paginated page of the current user's
    authentication history.

    Args:
        token (str): The current user's JWT access token.
        page (int): 1-indexed page number.
        page_size (int): Number of records per page.
        event_type (Optional[str]): Optional event type filter.

    Returns:
        Tuple[bool, Any]: (True, {"total": int, "records": [...]}) on
            success, or (False, error_message) on failure.
    """
    url = f"{BASE_URL}/history"
    params = {"page": page, "page_size": page_size}
    if event_type:
        params["event_type"] = event_type
    try:
        response = requests.get(
            url, headers=_build_headers(token), params=params, timeout=DEFAULT_TIMEOUT
        )
        return _handle_response(response)
    except requests.exceptions.ConnectionError:
        return False, "Could not connect to the backend server. Is it running?"
    except requests.exceptions.Timeout:
        return False, "The request timed out. Please try again."


def get_alerts(
    token: str,
    page: int = 1,
    page_size: int = 10,
    severity: Optional[str] = None,
    unread_only: bool = False,
) -> Tuple[bool, Any]:
    """
    Calls GET /alerts to retrieve a paginated page of the current user's
    alerts.

    Args:
        token (str): The current user's JWT access token.
        page (int): 1-indexed page number.
        page_size (int): Number of records per page.
        severity (Optional[str]): Optional severity filter.
        unread_only (bool): If True, only unread alerts are returned.

    Returns:
        Tuple[bool, Any]: (True, {"total": ..., "unread_count": ...,
            "alerts": [...]}) on success, or (False, error_message) on
            failure.
    """
    url = f"{BASE_URL}/alerts"
    params = {"page": page, "page_size": page_size, "unread_only": unread_only}
    if severity:
        params["severity"] = severity
    try:
        response = requests.get(
            url, headers=_build_headers(token), params=params, timeout=DEFAULT_TIMEOUT
        )
        return _handle_response(response)
    except requests.exceptions.ConnectionError:
        return False, "Could not connect to the backend server. Is it running?"
    except requests.exceptions.Timeout:
        return False, "The request timed out. Please try again."


def mark_alerts_read(token: str, alert_ids: List[str]) -> Tuple[bool, Any]:
    """
    Calls POST /alerts/read to mark one or more alerts as read.

    Args:
        token (str): The current user's JWT access token.
        alert_ids (List[str]): List of alert ID strings to mark as read.

    Returns:
        Tuple[bool, Any]: (True, confirmation_data) on success, or
            (False, error_message) on failure.
    """
    url = f"{BASE_URL}/alerts/read"
    payload = {"alert_ids": alert_ids}
    try:
        response = requests.post(
            url, json=payload, headers=_build_headers(token), timeout=DEFAULT_TIMEOUT
        )
        return _handle_response(response)
    except requests.exceptions.ConnectionError:
        return False, "Could not connect to the backend server. Is it running?"
    except requests.exceptions.Timeout:
        return False, "The request timed out. Please try again."


def get_latest_risk_score(token: str) -> Tuple[bool, Any]:
    """
    Calls GET /risk/latest to retrieve the current user's most recent
    risk score / AI prediction record (placeholder until AI integration).

    Args:
        token (str): The current user's JWT access token.

    Returns:
        Tuple[bool, Any]: (True, risk_data) on success, or
            (False, error_message) on failure.
    """
    url = f"{BASE_URL}/risk/latest"
    try:
        response = requests.get(
            url, headers=_build_headers(token), timeout=DEFAULT_TIMEOUT
        )
        return _handle_response(response)
    except requests.exceptions.ConnectionError:
        return False, "Could not connect to the backend server. Is it running?"
    except requests.exceptions.Timeout:
        return False, "The request timed out. Please try again."


def get_risk_score_history(token: str, limit: int = 30) -> Tuple[bool, Any]:
    """
    Calls GET /risk/history to retrieve a chronological series of the
    current user's risk score records, used to power Graphs (Requirement #8).

    Args:
        token (str): The current user's JWT access token.
        limit (int): Maximum number of records to retrieve.

    Returns:
        Tuple[bool, Any]: (True, list_of_risk_records) on success, or
            (False, error_message) on failure.
    """
    url = f"{BASE_URL}/risk/history"
    params = {"limit": limit}
    try:
        response = requests.get(
            url, headers=_build_headers(token), params=params, timeout=DEFAULT_TIMEOUT
        )
        return _handle_response(response)
    except requests.exceptions.ConnectionError:
        return False, "Could not connect to the backend server. Is it running?"
    except requests.exceptions.Timeout:
        return False, "The request timed out. Please try again."