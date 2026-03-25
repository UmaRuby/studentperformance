import streamlit as st
import pandas as pd
import os

def student_panel():
    st.title("🎓 Student Panel")

    # -----------------------------
    # CHECK DATASET UPLOAD
    # -----------------------------
    if "data" not in st.session_state:
        st.error("⚠️ No dataset found. Ask admin to upload dataset first.")
        st.stop()

    data = st.session_state["data"].copy()
    data = data.fillna("Not Available")

    for col in data.columns:
        data[col] = data[col].astype(str).str.strip()

    # -----------------------------
    # STUDENT DETAILS
    # -----------------------------
    st.subheader("🔍 View Your Details")
    sid = st.text_input("Enter Student ID")
    id_cols = [col for col in data.columns if "id" in col.lower()]

    uploaded_file_name = st.session_state.get("uploaded_file_name","default_dataset")
    feedback_file = f"feedback_{uploaded_file_name}.csv"

    # Load feedback CSV for this dataset
    if os.path.exists(feedback_file):
        feedback_df = pd.read_csv(feedback_file)
    else:
        feedback_df = pd.DataFrame(columns=["Student_ID","Feedback"])

    # -----------------------------
    # SHOW STUDENT DATA
    # -----------------------------
    if sid and len(id_cols) > 0:
        id_col = id_cols[0]
        data[id_col] = data[id_col].astype(str)
        student = data[data[id_col] == sid.strip()]

        if not student.empty:
            st.success("Student Found ✅")
            st.dataframe(student, use_container_width=True)

            # -----------------------------
            # SUBMIT FEEDBACK
            # -----------------------------
            st.subheader("💬 Submit Feedback")
            feedback = st.text_area("Write your feedback here:")

            if st.button("Submit Feedback"):
                if not feedback.strip():
                    st.warning("Feedback cannot be empty")
                else:
                    # Append feedback to CSV
                    new_feedback = pd.DataFrame([{"Student_ID": sid.strip(), "Feedback": feedback.strip()}])
                    feedback_df = pd.concat([feedback_df, new_feedback], ignore_index=True)
                    feedback_df.to_csv(feedback_file, index=False, encoding='utf-8')
                    st.success("Feedback submitted successfully ✅")

            # -----------------------------
            # SHOW PREVIOUS FEEDBACK
            # -----------------------------
            st.subheader("📋 Your Previous Feedback")
            student_feedback = feedback_df[feedback_df["Student_ID"] == sid.strip()]
            if not student_feedback.empty:
                st.dataframe(student_feedback[["Feedback"]], use_container_width=True)
            else:
                st.info("No feedback submitted yet.")

        else:
            st.error("Student not found ❌")

    if st.checkbox("Show Dataset Preview"):
        st.dataframe(data.head(20), use_container_width=True)