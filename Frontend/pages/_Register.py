"""
2_Register.py

Streamlit page implementing the User Registration screen
(Requirement #1: User Registration).

Presents a form collecting username, email, full name, and password
(with confirmation). On successful registration, informs the user and
directs them to the Login page to sign in with their new credentials.

This file is automatically picked up by Streamlit's multipage app system
because it lives inside the frontend/pages/ directory. The "2_" prefix
controls its position in the sidebar navigation order, placing it right
after the Login page.
"""

import streamlit as st

from Frontend.utils import api_client
from Frontend.app import init_session_state, render_sidebar_status

st.set_page_config(page_title="Register | Behavioral Biometrics Platform", page_icon="📝")

init_session_state()
render_sidebar_status()

st.title("📝 Create an Account")

# If the user is already authenticated, there's no reason to show a
# registration form — guide them to the Dashboard instead.
if st.session_state.get("is_authenticated"):
    st.success(f"You are already logged in as **{st.session_state.get('username')}**.")
    st.page_link("pages/3_Dashboard.py", label="Go to Dashboard", icon="📊")
    st.stop()

st.markdown("Fill in your details below to create a new account.")

with st.form("register_form", clear_on_submit=False):
    full_name = st.text_input("Full Name", placeholder="e.g. John Doe")
    username = st.text_input(
        "Username",
        placeholder="Choose a unique username (min. 3 characters)",
    )
    email = st.text_input("Email Address", placeholder="e.g. john.doe@example.com")
    password = st.text_input(
        "Password",
        type="password",
        placeholder="Minimum 6 characters",
    )
    confirm_password = st.text_input(
        "Confirm Password",
        type="password",
        placeholder="Re-enter your password",
    )

    submitted = st.form_submit_button("Register", use_container_width=True)

if submitted:
    # --- Client-side validation (fast feedback, before hitting the API) ---
    if not full_name or not username or not email or not password or not confirm_password:
        st.error("Please fill in all fields.")
    elif len(username) < 3:
        st.error("Username must be at least 3 characters long.")
    elif len(password) < 6:
        st.error("Password must be at least 6 characters long.")
    elif password != confirm_password:
        st.error("Passwords do not match. Please re-enter them.")
    elif "@" not in email or "." not in email:
        st.error("Please enter a valid email address.")
    else:
        with st.spinner("Creating your account..."):
            success, result = api_client.register_user(
                username=username,
                email=email,
                full_name=full_name,
                password=password,
            )

        if success:
            # result is the UserResponseSchema payload:
            # {"id": ..., "username": ..., "email": ..., "full_name": ...,
            #  "created_at": ..., "is_active": ...}
            st.success(
                f"🎉 Account created successfully for **{result['username']}**! "
                f"You can now log in."
            )
            st.page_link("pages/1_Login.py", label="Go to Login", icon="🔑")
        else:
            # result is a string error message, e.g. "Username is already
            # taken." or "Email is already registered."
            st.error(f"Registration failed: {result}")

st.markdown("---")
st.markdown("Already have an account?")
st.page_link("pages/1_Login.py", label="Log In Instead", icon="🔑")