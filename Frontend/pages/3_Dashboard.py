"""
3_Dashboard.py

Streamlit page implementing the main Dashboard screen (Requirement #3:
Dashboard).

Displays an at-a-glance summary of the authenticated user's account
activity: total logins, failed login attempts, alert counts, last login
time, and the current (placeholder) risk level / AI prediction status.

Protected page: calls require_login() first, so unauthenticated visitors
are redirected to the Login page instead of seeing any content here.
"""

import streamlit as st

from utils import api_client
from app import init_session_state, render_sidebar_status, require_login

st.set_page_config(page_title="Dashboard | Behavioral Biometrics Platform", page_icon="📊", layout="wide")

init_session_state()
require_login()
render_sidebar_status()

st.title("📊 Dashboard")
st.markdown(f"Welcome back, **{st.session_state.get('full_name')}**.")
st.markdown("---")

token = st.session_state.get("access_token")

with st.spinner("Loading your dashboard..."):
    success, result = api_client.get_dashboard_summary(token)

if not success:
    st.error(f"Could not load dashboard data: {result}")
    st.stop()

# --- Top-level metric cards ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Total Successful Logins", value=result["total_logins"])

with col2:
    st.metric(label="Failed Login Attempts", value=result["failed_login_attempts"])

with col3:
    st.metric(label="Total Alerts", value=result["total_alerts"])

with col4:
    st.metric(
        label="Unread Alerts",
        value=result["unread_alerts"],
        delta=None if result["unread_alerts"] == 0 else f"{result['unread_alerts']} new",
        delta_color="inverse",
    )

st.markdown("---")

# --- Secondary info: last login + risk/AI placeholder status ---
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🕒 Last Login")
    if result.get("last_login"):
        st.info(f"Your last successful login was at:\n\n**{result['last_login']}**")
    else:
        st.info("No successful logins recorded yet.")

with col_right:
    st.subheader("🧠 Risk Level & AI Prediction")
    risk_level = result.get("current_risk_level", "UNKNOWN")
    ai_prediction = result.get("latest_ai_prediction")

    if risk_level == "UNKNOWN":
        st.warning(
            "⏳ **Risk Level: Unknown** — the AI behavioral analysis model "
            "has not been integrated yet. This section will populate "
            "automatically once the AI model is connected by the team."
        )
    elif risk_level == "LOW":
        st.success(f"✅ **Risk Level: {risk_level}**")
    elif risk_level == "MEDIUM":
        st.warning(f"⚠️ **Risk Level: {risk_level}**")
    else:
        st.error(f"🚨 **Risk Level: {risk_level}**")

    if ai_prediction:
        st.write(f"**Latest AI Prediction:** {ai_prediction}")
    else:
        st.caption("AI Prediction: Not yet available (pending model integration).")

st.markdown("---")

# --- Quick navigation shortcuts ---
st.subheader("Quick Links")
nav_col1, nav_col2, nav_col3 = st.columns(3)
with nav_col1:
    st.page_link("pages/4_Authentication_History.py", label="View Authentication History", icon="📜")
with nav_col2:
    st.page_link("pages/5_Alerts.py", label="View Alerts", icon="🚨")
with nav_col3:
    st.page_link("pages/6_Risk_Score.py", label="View Risk Score & Graphs", icon="📈")