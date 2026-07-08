"""
5_Alerts.py

Streamlit page implementing the Alerts screen (Requirement #5: Alerts
Page).

Displays a paginated, filterable list of security alerts generated for
the current user (currently only from simple rule-based logic, e.g.
repeated failed logins — reserved fields exist for future AI-generated
alerts). Users can filter by severity and unread status, and mark alerts
as read individually or all at once.

Protected page: calls require_login() first.
"""

import streamlit as st
import pandas as pd

from utils import api_client
from app import init_session_state, render_sidebar_status, require_login

st.set_page_config(page_title="Alerts | Behavioral Biometrics Platform", page_icon="🚨", layout="wide")

init_session_state()
require_login()
render_sidebar_status()

st.title("🚨 Alerts")
st.markdown(
    "Security alerts generated for your account. Alerts marked "
    "**RULE_ENGINE** are produced by simple threshold-based logic today; "
    "alerts marked **AI_MODEL** are reserved for future behavioral "
    "biometrics detections once the AI team integrates their model."
)
st.markdown("---")

token = st.session_state.get("access_token")

if "alerts_page" not in st.session_state:
    st.session_state["alerts_page"] = 1

# ---------------------------------------------------------------------------
# Filter controls
# ---------------------------------------------------------------------------
filter_col1, filter_col2, filter_col3 = st.columns([1, 1, 1])

with filter_col1:
    severity_label_map = {
        "All Severities": None,
        "Low": "LOW",
        "Medium": "MEDIUM",
        "High": "HIGH",
    }
    selected_severity_label = st.selectbox("Filter by severity", options=list(severity_label_map.keys()))
    selected_severity = severity_label_map[selected_severity_label]

with filter_col2:
    unread_only = st.checkbox("Show unread only")

with filter_col3:
    page_size = st.selectbox("Alerts per page", options=[10, 25, 50, 100], index=0)

# ---------------------------------------------------------------------------
# Fetch data
# ---------------------------------------------------------------------------
with st.spinner("Loading alerts..."):
    success, result = api_client.get_alerts(
        token=token,
        page=st.session_state["alerts_page"],
        page_size=page_size,
        severity=selected_severity,
        unread_only=unread_only,
    )

if not success:
    st.error(f"Could not load alerts: {result}")
    st.stop()

total_alerts = result["total"]
unread_count = result["unread_count"]
alerts = result["alerts"]

# ---------------------------------------------------------------------------
# Summary metrics
# ---------------------------------------------------------------------------
metric_col1, metric_col2 = st.columns(2)
with metric_col1:
    st.metric("Total Alerts (this filter)", total_alerts)
with metric_col2:
    st.metric("Unread Alerts (account-wide)", unread_count)

st.markdown("---")

# ---------------------------------------------------------------------------
# Mark-all-as-read button
# ---------------------------------------------------------------------------
if alerts:
    unread_ids_on_page = [a["id"] for a in alerts if not a["is_read"]]
    if unread_ids_on_page:
        if st.button(f"✅ Mark all {len(unread_ids_on_page)} unread alerts on this page as read"):
            with st.spinner("Updating alerts..."):
                mark_success, mark_result = api_client.mark_alerts_read(token, unread_ids_on_page)
            if mark_success:
                st.success("Alerts marked as read.")
                st.rerun()
            else:
                st.error(f"Could not update alerts: {mark_result}")

# ---------------------------------------------------------------------------
# Display alerts
# ---------------------------------------------------------------------------
if not alerts:
    st.info("No alerts found for this filter. 🎉")
else:
    severity_icon_map = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🔴"}

    for alert in alerts:
        icon = severity_icon_map.get(alert["severity"], "⚪")
        read_label = "" if alert["is_read"] else " 🆕"

        with st.expander(
            f"{icon} [{alert['severity']}] {alert['alert_type'].replace('_', ' ').title()}{read_label} — {alert['created_at']}"
        ):
            st.write(f"**Message:** {alert['message']}")
            st.write(f"**Source:** {alert['source']}")
            st.write(f"**Status:** {'Read' if alert['is_read'] else 'Unread'}")

            if not alert["is_read"]:
                if st.button("Mark as read", key=f"mark_read_{alert['id']}"):
                    with st.spinner("Updating..."):
                        mark_success, mark_result = api_client.mark_alerts_read(token, [alert["id"]])
                    if mark_success:
                        st.rerun()
                    else:
                        st.error(f"Could not update alert: {mark_result}")

    # -----------------------------------------------------------------
    # Pagination controls
    # -----------------------------------------------------------------
    total_pages = max(1, (total_alerts + page_size - 1) // page_size)

    st.markdown("---")
    page_nav_col1, page_nav_col2, page_nav_col3 = st.columns([1, 2, 1])

    with page_nav_col1:
        if st.button("⬅️ Previous Page", disabled=(st.session_state["alerts_page"] <= 1)):
            st.session_state["alerts_page"] -= 1
            st.rerun()

    with page_nav_col2:
        st.markdown(
            f"<div style='text-align: center;'>Page {st.session_state['alerts_page']} of {total_pages}</div>",
            unsafe_allow_html=True,
        )

    with page_nav_col3:
        if st.button("Next Page ➡️", disabled=(st.session_state["alerts_page"] >= total_pages)):
            st.session_state["alerts_page"] += 1
            st.rerun()