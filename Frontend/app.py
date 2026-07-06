"""
app.py

Entry point for the Streamlit frontend of the Deep Behavioral Biometrics
Authentication Platform.

Responsibilities:
    - Initializes Streamlit's session_state with default values for
      authentication (token, username, login status).
    - Acts as the "gate": if the user is not logged in, only the
      Login/Register pages are meaningfully usable; if logged in, the
      full app (Dashboard, History, Alerts, Risk Score) is available.
    - Renders a persistent sidebar showing login status and a logout
      button once authenticated.
    - Provides the shared `require_login()` helper that every protected
      page imports and calls at the top of its script, so unauthenticated
      users are redirected back to the login flow instead of seeing
      protected content or a broken page full of errors.

Run this application with:
    streamlit run frontend/app.py

Streamlit automatically discovers files in the frontend/pages/ folder
and renders them as additional pages in the sidebar navigation menu.
"""

import streamlit as st

from Frontend.utils import api_client

# ---------------------------------------------------------------------------
# Page configuration (must be the first Streamlit command executed)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Deep Behavioral Biometrics Authentication Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


def init_session_state() -> None:
    """
    Initializes all session_state keys used across the application with
    safe default values, if they don't already exist.

    Streamlit's session_state persists across page navigations within the
    same browser session, but is reset if the browser tab is closed or
    the server restarts — acting as a simple, appropriate substitute for
    server-side session storage in this infrastructure-focused project.

    Keys initialized:
        - is_authenticated (bool): Whether a user is currently logged in.
        - access_token (Optional[str]): The current JWT, if logged in.
        - username (Optional[str]): The current user's username.
        - full_name (Optional[str]): The current user's display name.
        - user_id (Optional[str]): The current user's MongoDB ObjectId string.
    """
    defaults = {
        "is_authenticated": False,
        "access_token": None,
        "username": None,
        "full_name": None,
        "user_id": None,
    }
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def require_login() -> bool:
    """
    Guard function that protected pages call at the very top of their
    script to enforce that only authenticated users can view them.

    Returns:
        bool: True if the user is authenticated and the calling page
            should continue rendering. False if the user is not
            authenticated (in which case this function has already
            rendered a warning message and stopped further execution).
    """
    init_session_state()

    if not st.session_state["is_authenticated"]:
        st.warning("🔒 Please log in to access this page.")
        st.info("Use the sidebar to navigate to the **Login** page.")
        st.stop()  # Halts execution of the calling page immediately.
        return False

    return True


def render_sidebar_status() -> None:
    """
    Renders a small persistent status panel in the sidebar showing who is
    currently logged in (if anyone), and a logout button.

    This appears on every page since Streamlit renders app.py's top-level
    code once per session and the sidebar persists across the multipage
    navigation, but for reliability, each individual page also imports
    and calls this function so the status panel is always accurate
    regardless of which page the user is currently viewing.
    """
    with st.sidebar:
        st.markdown("---")
        if st.session_state.get("is_authenticated"):
            st.success(f"Logged in as **{st.session_state.get('username')}**")
            if st.button("🚪 Logout", use_container_width=True):
                logout()
        else:
            st.info("Not logged in.")


def logout() -> None:
    """
    Logs the current user out.

    Calls the backend's /auth/logout endpoint to record the logout event
    for the Authentication History page, then clears all authentication-
    related session_state values regardless of whether the API call
    succeeded (since the frontend session should end even if, say, the
    network briefly drops) and forces a rerun so the UI immediately
    reflects the logged-out state.
    """
    token = st.session_state.get("access_token")
    if token:
        api_client.logout_user(token)

    st.session_state["is_authenticated"] = False
    st.session_state["access_token"] = None
    st.session_state["username"] = None
    st.session_state["full_name"] = None
    st.session_state["user_id"] = None

    st.success("You have been logged out.")
    st.rerun()


# ---------------------------------------------------------------------------
# Main landing page content
# ---------------------------------------------------------------------------
def main() -> None:
    init_session_state()
    render_sidebar_status()

    st.title("🛡️ Deep Behavioral Biometrics Authentication Platform")
    st.markdown(
        """
        Welcome to the **Deep Behavioral Biometrics Authentication Platform** —
        a security-focused system that monitors authentication activity and
        (in a future phase) analyzes behavioral patterns to detect anomalous
        or fraudulent access attempts.
        """
    )

    st.markdown("---")

    if st.session_state["is_authenticated"]:
        st.subheader(f"Welcome back, {st.session_state.get('full_name')} 👋")
        st.write(
            "Use the sidebar to navigate to your **Dashboard**, "
            "**Authentication History**, **Alerts**, or **Risk Score** pages."
        )
    else:
        st.subheader("Get Started")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Already have an account?")
            st.page_link("pages/1_Login.py", label="Go to Login", icon="🔑")
        with col2:
            st.markdown("#### New here?")
            st.page_link("pages/2_Register.py", label="Create an Account", icon="📝")

    st.markdown("---")
    st.caption(
        "Project Module: Frontend, Backend & Database Infrastructure. "
        "AI-driven risk scoring will be integrated in a future phase."
    )


if __name__ == "__main__":
    main()
else:
    # Streamlit re-executes the script top-to-bottom on every interaction,
    # and imports app.py's module-level code the same way when run via
    # `streamlit run`, so we also call main() here to ensure it renders
    # correctly under Streamlit's actual execution model.
    main()