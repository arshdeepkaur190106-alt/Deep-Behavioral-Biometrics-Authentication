"""
4_Authentication_History.py

Streamlit page implementing the Authentication History screen
(Requirement #4: Authentication History).

Displays a paginated, filterable table of the current user's login and
logout events, sourced from GET /history. Users can filter by event type
(all / successful logins / failed logins / logouts) and page through
their full history.

Protected page: calls require_login() first.
"""

import streamlit as st
import pandas as pd

from utils import api_client
from app import init_session_state, render_sidebar_status, require_login

st.set_page_config(
    page_title="Authentication History | Behavioral Biometrics Platform",
    page_icon="📜",
    layout="wide",
)

init_session_state()
require_login()
render_sidebar_status()

st.title("📜 Authentication History")
st.markdown(
    "This page shows a complete, chronological record of every login and "
    "logout event on your account — the audit trail used for security "
    "monitoring and (in future) as input for behavioral risk analysis."
)
st.markdown("---")

token = st.session_state.get("access_token")

# ---------------------------------------------------------------------------
# Filter controls
# ---------------------------------------------------------------------------
filter_col1, filter_col2, filter_col3 = st.columns([2, 1, 1])

with filter_col1:
    event_type_label_map = {
        "All Events": None,
        "Successful Logins": "LOGIN_SUCCESS",
        "Failed Logins": "LOGIN_FAILED",
        "Logouts": "LOGOUT",
    }
    selected_label = st.selectbox("Filter by event type", options=list(event_type_label_map.keys()))
    selected_event_type = event_type_label_map[selected_label]

with filter_col2:
    page_size = st.selectbox("Records per page", options=[10, 25, 50, 100], index=0)

with filter_col3:
    # Initialize the current page number in session_state so it persists
    # across reruns triggered by filter changes, but reset it to 1 if the
    # filter selection changes (handled below).
    if "history_page" not in st.session_state:
        st.session_state["history_page"] = 1

# ---------------------------------------------------------------------------
# Fetch data for the current page/filter
# ---------------------------------------------------------------------------
with st.spinner("Loading authentication history..."):
    success, result = api_client.get_auth_history(
        token=token,
        page=st.session_state["history_page"],
        page_size=page_size,
        event_type=selected_event_type,
    )

if not success:
    st.error(f"Could not load authentication history: {result}")
    st.stop()

total_records = result["total"]
records = result["records"]

st.markdown(f"**Total matching records:** {total_records}")

# ---------------------------------------------------------------------------
# Display table
# ---------------------------------------------------------------------------
if not records:
    st.info("No authentication history records found for this filter.")
else:
    table_rows = []
    for record in records:
        event_type = record["event_type"]

        # Add a small visual icon per event type for quick scanning.
        if event_type == "LOGIN_SUCCESS":
            icon = "✅"
        elif event_type == "LOGIN_FAILED":
            icon = "❌"
        else:
            icon = "🚪"

        table_rows.append(
            {
                "Event": f"{icon} {event_type.replace('_', ' ').title()}",
                "Timestamp (UTC)": record["timestamp"],
                "IP Address": record.get("ip_address") or "Unknown",
                "Device / User-Agent": record.get("device_info") or "Unknown",
                "Risk Score": (
                    record["risk_score"] if record.get("risk_score") is not None else "Pending AI Integration"
                ),
            }
        )

    df = pd.DataFrame(table_rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # -----------------------------------------------------------------
    # Pagination controls
    # -----------------------------------------------------------------
    total_pages = max(1, (total_records + page_size - 1) // page_size)

    st.markdown("---")
    page_nav_col1, page_nav_col2, page_nav_col3 = st.columns([1, 2, 1])

    with page_nav_col1:
        if st.button("⬅️ Previous Page", disabled=(st.session_state["history_page"] <= 1)):
            st.session_state["history_page"] -= 1
            st.rerun()

    with page_nav_col2:
        st.markdown(
            f"<div style='text-align: center;'>Page {st.session_state['history_page']} of {total_pages}</div>",
            unsafe_allow_html=True,
        )

    with page_nav_col3:
        if st.button(
            "Next Page ➡️",
            disabled=(st.session_state["history_page"] >= total_pages),
        ):
            st.session_state["history_page"] += 1
            st.rerun()