# Deep-Behavioral-Biometrics-Authentication
AI-powered continuous authentication system using behavioral biometrics, machine learning, and cybersecurity techniques.
# Deep Behavioral Biometrics Authentication Platform

A full-stack authentication monitoring platform built as a college project.
This repository contains the **frontend, backend, and database infrastructure**
(developed by Member 1). AI-driven behavioral biometrics analysis (CNN/LSTM
model, risk prediction logic) will be integrated separately by other team
members into the placeholder endpoints already provided here.

---

## 📌 Project Overview

This platform monitors user authentication activity and provides the
infrastructure for future AI-based behavioral risk analysis. It currently
implements:

1. **User Registration** — secure account creation with hashed passwords.
2. **Login Authentication** — JWT-based session authentication.
3. **Dashboard** — aggregated account activity summary.
4. **Authentication History** — full audit trail of login/logout events.
5. **Alerts Page** — rule-based security alerts (e.g. repeated failed logins).
6. **Risk Score placeholder** — data structure and API ready for AI integration.
7. **AI Prediction placeholder** — data structure and API ready for AI integration.
8. **Graphs** — interactive visualizations of activity and (future) risk trends.
9. **Logout** — session termination with audit logging.

> **Important:** No AI/ML logic (CNN, LSTM, TensorFlow, PyTorch, or any
> prediction algorithm) exists anywhere in this codebase. All risk score
> and AI prediction fields are honest placeholders (`null` / `"UNKNOWN"`)
> until the AI/ML team integrates their model.

---

## 🛠️ Technology Stack

| Layer      | Technology                          |
|------------|--------------------------------------|
| Frontend   | Streamlit                            |
| Backend    | FastAPI (Python, async)              |
| Database   | MongoDB (via Motor async driver)     |
| Auth       | JWT (python-jose) + bcrypt (passlib) |
| Language   | Python 3.11+ only                    |

---

## 📁 Project Structure