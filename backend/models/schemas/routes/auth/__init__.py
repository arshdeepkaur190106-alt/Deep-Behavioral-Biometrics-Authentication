"""
auth package

Contains security-related utilities: password hashing (hashing.py) and
JWT token creation/verification (jwt_handler.py). Kept separate from
routes/ so security-critical logic is isolated and easy to review/test
independently.
"""