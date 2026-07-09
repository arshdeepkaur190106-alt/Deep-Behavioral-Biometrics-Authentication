"""
auth_routes.py

Implements the core authentication endpoints for the Deep Behavioral
Biometrics Authentication Platform:

    - POST /auth/register  : Create a new user account.
    - POST /auth/login     : Authenticate a user and issue a JWT token.
    - POST /auth/logout    : Log a logout event (JWT itself is stateless
                              and invalidated client-side by discarding it).

Also defines `get_current_user`, a reusable FastAPI dependency that other
route modules (dashboard, history, alerts, risk) import to protect their
endpoints — ensuring only requests with a valid JWT can access them.

Every login attempt (success or failure) and every logout is recorded in
the `auth_history` collection, which powers Requirement #4 (Authentication
History) and feeds Requirement #6 (Risk Score placeholder).

This file also contains simple, transparent RULE-BASED alert generation
(e.g., flagging repeated failed login attempts). This is NOT AI/ML logic —
it is plain conditional logic your teammates' AI model will later
supplement, not replace.
"""


from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer

from backend.database import users_collection, auth_history_collection, alerts_collection
from backend.models.user_model import UserModel
from backend.models.auth_history_model import AuthHistoryModel
from backend.models.alert_model import AlertModel
from backend.models.schemas.user_schema import (
    UserRegisterSchema,
    UserLoginSchema,
    UserResponseSchema,
    TokenResponseSchema,
)
from backend.models.schemas.routes.auth.hashing import (
    hash_password,
    verify_password,
)
from backend.models.schemas.routes.auth.jwt_handler import (
    create_access_token,
    decode_access_token,
)
from backend.models.schemas.routes.auth.utils.helpers import (
    get_client_ip,
    get_device_info,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

# ---------------------------------------------------------------------------
# OAuth2 scheme (tells FastAPI/Swagger how to collect the Bearer token)
# ---------------------------------------------------------------------------
# tokenUrl points Swagger's "Authorize" button to the login endpoint so the
# interactive docs can be used to obtain and apply a token in one place.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ---------------------------------------------------------------------------
# Event type constants (avoids typos/inconsistency across the codebase)
# ---------------------------------------------------------------------------
EVENT_LOGIN_SUCCESS = "LOGIN_SUCCESS"
EVENT_LOGIN_FAILED = "LOGIN_FAILED"
EVENT_LOGOUT = "LOGOUT"

# Simple rule-based threshold: if a user racks up this many consecutive
# failed logins, a security alert is generated. This is plain conditional
# logic, NOT an AI/ML model.
FAILED_LOGIN_ALERT_THRESHOLD = 3


# ---------------------------------------------------------------------------
# Dependency: get_current_user
# ---------------------------------------------------------------------------

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserModel:
    """
    FastAPI dependency that extracts and validates the current user from
    the JWT provided in the Authorization header.

    Used by every protected route (dashboard, history, alerts, risk) via
    `Depends(get_current_user)`. Raises a 401 error if the token is
    missing, invalid, expired, or refers to a user that no longer exists.

    Args:
        token (str): Automatically extracted from the "Authorization:
            Bearer <token>" header by the oauth2_scheme dependency.

    Returns:
        UserModel: The authenticated user's data.

    Raises:
        HTTPException: 401 Unauthorized if the token is invalid/expired,
            or if the referenced user cannot be found / is inactive.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    from bson import ObjectId
    from bson.errors import InvalidId

    try:
        object_id = ObjectId(user_id)
    except InvalidId:
        raise credentials_exception

    user_document = await users_collection.find_one({"_id": object_id})
    if user_document is None:
        raise credentials_exception

    user = UserModel.from_mongo_document(user_document)

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated.",
        )

    return user


# ---------------------------------------------------------------------------
# POST /auth/register
# ---------------------------------------------------------------------------

@router.post(
    "/register",
    response_model=UserResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
async def register(payload: UserRegisterSchema):
    """
    Registers a new user account.

    Steps:
        1. Check that the username is not already taken.
        2. Check that the email is not already taken.
        3. Hash the plaintext password (never stored in plaintext).
        4. Insert the new user document into MongoDB.
        5. Return the public-safe user profile (never the password hash).

    Raises:
        HTTPException 400: If the username or email is already registered.
    """
    existing_username = await users_collection.find_one({"username": payload.username})
    if existing_username is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username is already taken.",
        )

    existing_email = await users_collection.find_one({"email": payload.email})
    if existing_email is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered.",
        )

    hashed_pw = hash_password(payload.password)

    new_user = UserModel(
        username=payload.username,
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=hashed_pw,
    )

    insert_result = await users_collection.insert_one(new_user.to_mongo_dict())

    created_user_document = await users_collection.find_one({"_id": insert_result.inserted_id})
    created_user = UserModel.from_mongo_document(created_user_document)

    return UserResponseSchema(
        id=created_user.id,
        username=created_user.username,
        email=created_user.email,
        full_name=created_user.full_name,
        created_at=created_user.created_at,
        is_active=created_user.is_active,
    )


# ---------------------------------------------------------------------------
# POST /auth/login
# ---------------------------------------------------------------------------

@router.post(
    "/login",
    response_model=TokenResponseSchema,
    summary="Authenticate a user and receive a JWT access token",
)
async def login(payload: UserLoginSchema, request: Request):
    """
    Authenticates a user with username + password.

    On every attempt (successful or failed), an AuthHistoryModel record
    is created in MongoDB. On repeated failures, a rule-based security
    alert is generated (simple threshold logic, not AI).

    Steps:
        1. Look up the user by username.
        2. If not found, log a failed attempt and raise 401.
        3. Verify the password against the stored bcrypt hash.
        4. If incorrect, log a failed attempt, possibly raise an alert,
           and raise 401.
        5. If correct, log a success, issue a JWT, and return it.

    Raises:
        HTTPException 401: If username doesn't exist or password is wrong.
    """
    client_ip = get_client_ip(request)
    device_info = get_device_info(request)

    user_document = await users_collection.find_one({"username": payload.username})

    if user_document is None:
        # Log failed attempt even though we don't have a real user_id.
        # We use "unknown" as a marker since no matching account exists.
        failed_entry = AuthHistoryModel(
            user_id="unknown",
            username=payload.username,
            event_type=EVENT_LOGIN_FAILED,
            ip_address=client_ip,
            device_info=device_info,
        )
        await auth_history_collection.insert_one(failed_entry.to_mongo_dict())

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )

    user = UserModel.from_mongo_document(user_document)

    password_valid = verify_password(payload.password, user.hashed_password)

    if not password_valid:
        failed_entry = AuthHistoryModel(
            user_id=user.id,
            username=user.username,
            event_type=EVENT_LOGIN_FAILED,
            ip_address=client_ip,
            device_info=device_info,
        )
        await auth_history_collection.insert_one(failed_entry.to_mongo_dict())

        # --- Simple rule-based alert logic (NOT AI) ---
        # Count how many of the user's most recent history entries were
        # failed logins in a row, to decide whether to raise an alert.
        recent_cursor = auth_history_collection.find(
            {"user_id": user.id}
        ).sort("timestamp", -1).limit(FAILED_LOGIN_ALERT_THRESHOLD)
        recent_entries = await recent_cursor.to_list(length=FAILED_LOGIN_ALERT_THRESHOLD)

        consecutive_failures = 0
        for entry in recent_entries:
            if entry.get("event_type") == EVENT_LOGIN_FAILED:
                consecutive_failures += 1
            else:
                break

        if consecutive_failures >= FAILED_LOGIN_ALERT_THRESHOLD:
            alert = AlertModel(
                user_id=user.id,
                username=user.username,
                alert_type="MULTIPLE_FAILED_LOGINS",
                message=(
                    f"{FAILED_LOGIN_ALERT_THRESHOLD} or more consecutive failed "
                    f"login attempts detected for this account."
                ),
                severity="HIGH",
                source="RULE_ENGINE",
            )
            await alerts_collection.insert_one(alert.to_mongo_dict())

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )

    # --- Successful login ---
    success_entry = AuthHistoryModel(
        user_id=user.id,
        username=user.username,
        event_type=EVENT_LOGIN_SUCCESS,
        ip_address=client_ip,
        device_info=device_info,
    )
    await auth_history_collection.insert_one(success_entry.to_mongo_dict())

    access_token = create_access_token(data={"sub": user.id, "username": user.username})

    user_response = UserResponseSchema(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        created_at=user.created_at,
        is_active=user.is_active,
    )

    return TokenResponseSchema(
        access_token=access_token,
        token_type="bearer",
        user=user_response,
    )


# ---------------------------------------------------------------------------
# POST /auth/logout
# ---------------------------------------------------------------------------

@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Log out the current user",
)
async def logout(request: Request, current_user: UserModel = Depends(get_current_user)):
    """
    Logs a logout event for the currently authenticated user.

    Since JWTs are stateless, the server cannot forcibly "invalidate" the
    token itself without maintaining a blocklist (out of scope for this
    infrastructure-focused project). Instead, logout is handled by:
        1. Recording a LOGOUT event in the auth_history collection (for
           the Authentication History page).
        2. The Streamlit frontend discarding the token from its session
           state, which effectively ends the session client-side.

    Returns:
        dict: A simple confirmation message.
    """
    client_ip = get_client_ip(request)
    device_info = get_device_info(request)

    logout_entry = AuthHistoryModel(
        user_id=current_user.id,
        username=current_user.username,
        event_type=EVENT_LOGOUT,
        ip_address=client_ip,
        device_info=device_info,
    )
    await auth_history_collection.insert_one(logout_entry.to_mongo_dict())

    return {"message": f"User '{current_user.username}' logged out successfully."}