"""
1_Login.py

Streamlit page implementing the Login screen (Requirement #2: Login
Authentication).

Presents a simple username/password form. On successful authentication,
stores the returned JWT access token and user profile information into
st.session_state, then redirects the user to the Dashboard page.

This file is automatically picked up by Streamlit's multipage app system
because it lives inside the frontend/pages/ directory. The "1_" prefix
controls its position in the sidebar navigation order.
"""

import streamlit as st

from Frontend.utils import api_client
from Frontend.app import init_session_state, render_sidebar_status

st.set_page_config(page_title="Login | Behavioral Biometrics Platform", page_icon="🔑")

init_session_state()
render_sidebar_status()

st.title("🔑 Login")

# If the user is already authenticated, there's no need to show the login
# form again — guide them straight to the Dashboard instead.
if st.session_state.get("is_authenticated"):
    st.success(f"You are already logged in as **{st.session_state.get('username')}**.")
    st.page_link("pages/3_Dashboard.py", label="Go to Dashboard", icon="📊")
    st.stop()

st.markdown("Enter your credentials to access your account.")

with st.form("login_form", clear_on_submit=False):
    username = st.text_input("Username", placeholder="Enter your username")
    password = st.text_input("Password", type="password", placeholder="Enter your password")

    submitted = st.form_submit_button("Login", use_container_width=True)

if submitted:
    if not username or not password:
        st.error("Please enter both username and password.")
    else:
        with st.spinner("Authenticating..."):
            success, result = api_client.login_user(username, password)

        if success:
            # result is the TokenResponseSchema payload:
            # {"access_token": ..., "token_type": "bearer", "user": {...}}
            st.session_state["is_authenticated"] = True
            st.session_state["access_token"] = result["access_token"]
            st.session_state["username"] = result["user"]["username"]
            st.session_state["full_name"] = result["user"]["full_name"]
            st.session_state["user_id"] = result["user"]["id"]

            st.success(f"Welcome back, {result['user']['full_name']}! Redirecting...")
            st.switch_page("pages/3_Dashboard.py")
        else:
            # result is a string error message extracted from the
            # backend's {"detail": "..."} response, e.g. "Invalid
            # username or password."
            st.error(f"Login failed: {result}")

st.markdown("---")
st.markdown("Don't have an account yet?")
st.page_link("pages/2_Register.py", label="Create an Account", icon="📝")