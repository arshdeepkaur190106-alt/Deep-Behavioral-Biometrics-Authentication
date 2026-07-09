import time
import streamlit as st
import pandas as pd
import plotly.express as px
import requests

from utils import api_client
from app import init_session_state, render_sidebar_status, require_login

st.set_page_config(
    page_title="Risk Score & AI Prediction | Behavioral Biometrics Platform",
    page_icon="📈",
    layout="wide",
)

init_session_state()
require_login()
render_sidebar_status()

st.title("📈 Risk Score & AI Prediction")
st.markdown("This page calls the AI/ML backend and displays the behavioral risk prediction.")
st.markdown("---")

token = st.session_state.get("access_token")

# ---------------------------------------------------------------------------
# Real interaction tracking (Streamlit-native)
# ---------------------------------------------------------------------------
if "page_enter_time" not in st.session_state:
    st.session_state.page_enter_time = time.time()
    st.session_state.typed_text_prev = ""
    st.session_state.backspace_count = 0
    st.session_state.mouse_clicks = 0

st.subheader("🧠 Current Risk Assessment")
st.markdown("Type something below and move the slider a bit, then click a button.")

typed_text = st.text_area(
    "Type anything here (simulates keystroke capture)",
    key="typing_sample",
    height=100,
)

# Detect backspaces: if new text is shorter than before, count it as a correction
if typed_text != st.session_state.typed_text_prev:
    if len(typed_text) < len(st.session_state.typed_text_prev):
        st.session_state.backspace_count += 1
    st.session_state.typed_text_prev = typed_text

activity_slider = st.slider(
    "Move this slider a little (simulates mouse/scroll activity)",
    0, 100, 50, key="activity_slider"
)

if st.button("Register Click (simulates mouse click)"):
    st.session_state.mouse_clicks += 1

st.markdown("")
col_a, col_b = st.columns(2)

with col_a:
    run_normal = st.button("Run AI Risk Prediction (My Real Activity)", use_container_width=True)

with col_b:
    run_highrisk = st.button("⚠️ Simulate High-Risk Session (Demo)", use_container_width=True)

if run_normal or run_highrisk:

    if run_highrisk:
        behavior_data = {
            "sessionDuration": 8000,
            "totalKeyEvents": 520,
            "typingSpeed": 0.9,
            "averageHoldTime": 0.25,
            "averageFlightTime": 0.16,
            "backspaceCount": 11,
            "errorRate": 0.11,
            "totalMouseEvents": 370,
            "mouseClicks": 33,
            "doubleClicks": 7,
            "dragCount": 5,
            "averageMouseSpeed": 1.8,
            "averageMouseAcceleration": 0.8,
            "totalScrollEvents": 85,
            "totalScrollDistance": 2700,
            "averageScrollSpeed": 1.0,
            "maxScrollSpeed": 2.0,
            "minScrollSpeed": 0.35,
            "scrollUpCount": 27,
            "scrollDownCount": 24,
        }
    else:
        session_duration_ms = int((time.time() - st.session_state.page_enter_time) * 1000)
        total_key_events = len(typed_text)

        behavior_data = {
            "sessionDuration": session_duration_ms,
            "totalKeyEvents": total_key_events,
            "typingSpeed": round(total_key_events / max(session_duration_ms / 1000, 1), 2),
            "averageHoldTime": 0.14,
            "averageFlightTime": 0.09,
            "backspaceCount": st.session_state.backspace_count,
            "errorRate": round(st.session_state.backspace_count / max(total_key_events, 1), 2),
            "totalMouseEvents": st.session_state.mouse_clicks * 10,
            "mouseClicks": st.session_state.mouse_clicks,
            "doubleClicks": 0,
            "dragCount": 0,
            "averageMouseSpeed": 0.8,
            "averageMouseAcceleration": 0.3,
            "totalScrollEvents": activity_slider,
            "totalScrollDistance": activity_slider * 12,
            "averageScrollSpeed": 0.4,
            "maxScrollSpeed": 0.9,
            "minScrollSpeed": 0.1,
            "scrollUpCount": activity_slider // 5,
            "scrollDownCount": (100 - activity_slider) // 5,
        }

    try:
        response = requests.post(
            "http://127.0.0.1:8000/api/behavior",
            json=behavior_data,
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )

        if response.status_code == 200:
            result = response.json()
            prediction = result.get("prediction")
            confidence = result.get("confidence")
            risk_score = result.get("risk_score")

            metric_col1, metric_col2, metric_col3 = st.columns(3)
            with metric_col1:
                st.metric("AI Prediction", prediction)
            with metric_col2:
                st.metric("Confidence", f"{confidence}%")
            with metric_col3:
                st.metric("Risk Score", f"{risk_score}%")

            st.success("AI prediction received successfully from backend.")

            st.subheader("Behavioral Data Sent to Backend")
            st.json(behavior_data)

            st.subheader("Backend ML Response")
            st.json(result)
        else:
            st.error(f"Backend returned error code: {response.status_code}")
            st.text(response.text)

    except Exception as e:
        st.error("Could not connect to backend.")
        st.write(e)

st.markdown("---")

# ---------------------------------------------------------------------------
# Section 2: Risk Score History Graph
# ---------------------------------------------------------------------------
st.subheader("📊 Risk Score Trend Over Time")

history_limit = st.slider(
    "Number of most recent records to display",
    min_value=5, max_value=200, value=30, step=5,
)

with st.spinner("Loading risk score history..."):
    history_success, history_records = api_client.get_risk_score_history(token, limit=history_limit)

if not history_success:
    st.error(f"Could not load risk score history: {history_records}")
elif not history_records:
    st.info("📭 No risk score history is available yet.")
else:
    chart_rows = []
    for record in history_records:
        chart_rows.append({
            "Computed / Created At": record.get("computed_at") or record.get("created_at"),
            "Risk Score": record.get("risk_score") if record.get("risk_score") is not None else 0,
            "Risk Level": record.get("risk_level", "UNKNOWN"),
        })
    df = pd.DataFrame(chart_rows)
    fig = px.line(df, x="Computed / Created At", y="Risk Score", markers=True, title="Risk Score Over Time")
    fig.update_layout(yaxis_range=[0, 1], xaxis_title="Time", yaxis_title="Risk Score (0.0 – 1.0)")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("#### Risk Score History Table")
    st.dataframe(df, use_container_width=True, hide_index=True)

st.markdown("---")

# ---------------------------------------------------------------------------
# Section 3: Login Activity Overview
# ---------------------------------------------------------------------------
st.subheader("📊 Login Activity Overview")

with st.spinner("Loading account activity summary..."):
    dash_success, dash_result = api_client.get_dashboard_summary(token)

if dash_success:
    activity_df = pd.DataFrame({
        "Category": ["Successful Logins", "Failed Login Attempts", "Total Alerts", "Unread Alerts"],
        "Count": [
            dash_result["total_logins"],
            dash_result["failed_login_attempts"],
            dash_result["total_alerts"],
            dash_result["unread_alerts"],
        ],
    })
    bar_fig = px.bar(activity_df, x="Category", y="Count", color="Category", title="Account Activity Summary", text="Count")
    bar_fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Count")
    st.plotly_chart(bar_fig, use_container_width=True)
else:
    st.warning("Could not load account activity summary for the chart.")