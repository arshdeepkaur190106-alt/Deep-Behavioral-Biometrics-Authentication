"""
6_Risk_Score.py

Streamlit page implementing the Risk Score placeholder (Requirement #6),
AI Prediction placeholder (Requirement #7), and Graphs (Requirement #8).

Displays:
    - The user's most recent risk score / AI prediction status (currently
      always a placeholder, since no AI model is integrated yet).
    - A time-series graph of risk score history (will show "No data yet"
      until the AI model begins writing real records).

This page contains NO AI/ML computation. It only visualizes whatever
placeholder or (eventually) real data exists in the risk_scores
collection via the /risk/latest and /risk/history endpoints.

Protected page: calls require_login() first.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
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
st.markdown(
    "This page displays your account's behavioral risk assessment. "
    "**This feature is currently a placeholder** — the underlying AI "
    "model (CNN/LSTM-based behavioral biometrics analysis) has not yet "
    "been integrated by the AI/ML team. Once integrated, real risk "
    "scores and predictions will appear here automatically, with no "
    "changes needed to this page."
)
st.markdown("---")

token = st.session_state.get("access_token")

# ---------------------------------------------------------------------------
# Section 1: Latest Risk Score / AI Prediction
# ---------------------------------------------------------------------------
st.subheader("🧠 Current Risk Assessment")

with st.spinner("Loading latest risk assessment..."):
    success, latest = api_client.get_latest_risk_score(token)

if not success:
    st.error(f"Could not load risk score data: {latest}")
    st.stop()

risk_score = latest.get("risk_score")
risk_level = latest.get("risk_level", "UNKNOWN")
ai_prediction = latest.get("ai_prediction")
model_version = latest.get("model_version")
computed_at = latest.get("computed_at")

metric_col1, metric_col2, metric_col3 = st.columns(3)

with metric_col1:
    st.metric(
        label="Risk Score",
        value=f"{risk_score:.2f}" if risk_score is not None else "N/A",
    )

with metric_col2:
    level_display = {
        "UNKNOWN": "❓ Unknown",
        "LOW": "🟢 Low",
        "MEDIUM": "🟡 Medium",
        "HIGH": "🔴 High",
    }.get(risk_level, risk_level)
    st.metric(label="Risk Level", value=level_display)

with metric_col3:
    st.metric(label="AI Prediction", value=ai_prediction if ai_prediction else "Pending")

if risk_level == "UNKNOWN":
    st.info(
        "⏳ No AI-driven risk assessment has been computed yet for your "
        "account. This section is fully wired up and ready — it will "
        "populate automatically as soon as the AI model is connected "
        "and begins writing risk scores."
    )
else:
    detail_col1, detail_col2 = st.columns(2)
    with detail_col1:
        st.write(f"**Model Version:** {model_version or 'N/A'}")
    with detail_col2:
        st.write(f"**Computed At:** {computed_at or 'N/A'}")

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
    history_success, history_records = api_client.get_risk_score_history(token, limit=history_limit)

if not history_success:
    st.error(f"Could not load risk score history: {history_records}")
elif not history_records:
    st.info(
        "📭 No risk score history is available yet. Once the AI model "
        "begins computing and storing risk scores over time, this graph "
        "will automatically display the trend — no changes needed to "
        "this page when that integration happens."
    )
else:
    chart_rows = []
    for record in history_records:
        chart_rows.append(
            {
                "Computed / Created At": record.get("computed_at") or record.get("created_at"),
                "Risk Score": record.get("risk_score") if record.get("risk_score") is not None else 0,
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
        color_discrete_sequence=["#EF553B"],
    )
    fig.update_layout(yaxis_range=[0, 1], xaxis_title="Time", yaxis_title="Risk Score (0.0 – 1.0)")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Risk Score History Table")
    st.dataframe(df, use_container_width=True, hide_index=True)

st.markdown("---")

# ---------------------------------------------------------------------------
# Section 3: Login Activity Overview (built from Dashboard data as an
# additional graph, giving Requirement #8 a second, currently-functional
# chart even while risk score history is still empty)
# ---------------------------------------------------------------------------
st.subheader("📊 Login Activity Overview")

with st.spinner("Loading account activity summary..."):
    dash_success, dash_result = api_client.get_dashboard_summary(token)

if dash_success:
    activity_df = pd.DataFrame(
        {
            "Category": ["Successful Logins", "Failed Login Attempts", "Total Alerts", "Unread Alerts"],
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