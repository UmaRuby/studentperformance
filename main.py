import streamlit as st
from student_panel import student_panel
from admin_panel import admin_panel

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Student Performance System",
    layout="wide"
)

st.title("🎓 Student Performance System")

# -----------------------------
# SIDEBAR MENU
# -----------------------------
menu = st.sidebar.radio(
    "🔹 Login Menu",
    ["Home", "Student", "Admin"]
)

# -----------------------------
# MENU NAVIGATION
# -----------------------------
if menu == "Home":
    st.subheader("Welcome! Please select your role from the sidebar.")
elif menu == "Student":
    student_panel()
elif menu == "Admin":
    admin_panel()