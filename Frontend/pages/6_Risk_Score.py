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
# Section 1: AI Prediction from ML backend
# ---------------------------------------------------------------------------
st.subheader("🧠 Current Risk Assessment")

behavior_data = {
    "sessionDuration": 12000,
    "totalKeyEvents": 340,
    "typingSpeed": 0.52,
    "averageHoldTime": 0.14,
    "averageFlightTime": 0.09,
    "backspaceCount": 3,
    "errorRate": 0.02,
    "totalMouseEvents": 210,
    "mouseClicks": 15,
    "doubleClicks": 2,
    "dragCount": 1,
    "averageMouseSpeed": 0.8,
    "averageMouseAcceleration": 0.3,
    "totalScrollEvents": 45,
    "totalScrollDistance": 1200,
    "averageScrollSpeed": 0.4,
    "maxScrollSpeed": 0.9,
    "minScrollSpeed": 0.1,
    "scrollUpCount": 12,
    "scrollDownCount": 10,
}

if st.button("Run AI Risk Prediction", use_container_width=True):
    try:
        response = requests.post(
            "http://127.0.0.1:8000/api/behavior",
            json=behavior_data,
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
    min_value=5,
    max_value=200,
    value=30,
    step=5,
)

with st.spinner("Loading risk score history..."):
    history_success, history_records = api_client.get_risk_score_history(
        token, limit=history_limit
    )

if not history_success:
    st.error(f"Could not load risk score history: {history_records}")
elif not history_records:
    st.info("📭 No risk score history is available yet.")
else:
    chart_rows = []
    for record in history_records:
        chart_rows.append(
            {
                "Computed / Created At": record.get("computed_at")
                or record.get("created_at"),
                "Risk Score": record.get("risk_score")
                if record.get("risk_score") is not None
                else 0,
                "Risk Level": record.get("risk_level", "UNKNOWN"),
            }
        )

    df = pd.DataFrame(chart_rows)

    fig = px.line(
        df,
        x="Computed / Created At",
        y="Risk Score",
        markers=True,
        title="Risk Score Over Time",
    )
    fig.update_layout(
        yaxis_range=[0, 1],
        xaxis_title="Time",
        yaxis_title="Risk Score (0.0 – 1.0)",
    )
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
    activity_df = pd.DataFrame(
        {
            "Category": [
                "Successful Logins",
                "Failed Login Attempts",
                "Total Alerts",
                "Unread Alerts",
            ],
            "Count": [
                dash_result["total_logins"],
                dash_result["failed_login_attempts"],
                dash_result["total_alerts"],
                dash_result["unread_alerts"],
            ],
        }
    )

    bar_fig = px.bar(
        activity_df,
        x="Category",
        y="Count",
        color="Category",
        title="Account Activity Summary",
        text="Count",
    )
    bar_fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Count")
    st.plotly_chart(bar_fig, use_container_width=True)
else:
    st.warning("Could not load account activity summary for the chart.")