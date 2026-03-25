import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
import os

def admin_panel():
    st.title("🎓 Student Performance Admin Panel")

    # -----------------------------
    # LOGOUT BUTTON
    # -----------------------------
    if st.button("Logout"):
        st.session_state.clear()
        st.success("Logged out")
        st.rerun()

    # -----------------------------
    # UPLOAD DATASET
    # -----------------------------
    uploaded_file = st.file_uploader("📂 Upload CSV Dataset", type=["csv"])
    if uploaded_file:
        data = pd.read_csv(uploaded_file)
        data.columns = data.columns.str.strip()
        st.session_state["data"] = data.copy()
        st.session_state["uploaded_file_name"] = uploaded_file.name
        st.success("✅ Dataset Uploaded Successfully")
    elif "data" in st.session_state:
        data = st.session_state["data"]
    else:
        st.warning("Upload dataset to continue")
        st.stop()

    st.write(f"Rows: {data.shape[0]} | Columns: {data.shape[1]}")
    st.dataframe(data.head(10))

    # -----------------------------
    # AUTO DETECT COLUMNS
    # -----------------------------
    cgpa_col = next((c for c in data.columns if "cgpa" in c.lower()), None)
    attendance_col = next((c for c in data.columns if "attendance" in c.lower()), None)
    behaviour_col = next((c for c in data.columns if "behaviour" in c.lower() or "behavior" in c.lower()), None)

    if cgpa_col is None:
        st.error("❌ CGPA column not found")
        st.stop()

    # -----------------------------
    # MODEL DATA
    # -----------------------------
    model_data = pd.DataFrame()
    model_data["CGPA"] = pd.to_numeric(data[cgpa_col], errors='coerce')
    model_data["Attendance"] = pd.to_numeric(data[attendance_col], errors='coerce') if attendance_col else 75

    if behaviour_col:
        le = LabelEncoder()
        model_data["Behaviour"] = le.fit_transform(data[behaviour_col].astype(str))
    else:
        model_data["Behaviour"] = 1

    model_data = model_data.fillna(model_data.mean())

    # -----------------------------
    # PERFORMANCE
    # -----------------------------
    def performance(row):
        if row["Attendance"] < 40:
            return "Poor"
        att_level = "Excellent" if row["Attendance"] >= 85 else "Good" if row["Attendance"] >= 75 else "Average" if row["Attendance"] >= 60 else "Poor"
        if row["CGPA"] >= 8 and att_level in ["Excellent","Good"]: return "Excellent"
        elif row["CGPA"] >= 6.5 and att_level in ["Good","Average"]: return "Good"
        elif row["CGPA"] >=5: return "Average"
        else: return "Poor"

    model_data["Performance"] = model_data.apply(performance, axis=1)

    # -----------------------------
    # TRAIN MODELS
    # -----------------------------
    X = model_data[["CGPA","Attendance","Behaviour"]]
    y = model_data["Performance"]
    X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=0.2,random_state=42)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    lr = LogisticRegression(max_iter=2000)
    dt = DecisionTreeClassifier()
    rf = RandomForestClassifier()

    lr.fit(X_train_scaled, y_train)
    dt.fit(X_train, y_train)
    rf.fit(X_train, y_train)

    lr_pred = lr.predict(X_test_scaled)
    dt_pred = dt.predict(X_test)
    rf_pred = rf.predict(X_test)

    acc_lr = accuracy_score(y_test, lr_pred)
    acc_dt = accuracy_score(y_test, dt_pred)
    acc_rf = accuracy_score(y_test, rf_pred)

    # -----------------------------
    # MODEL COMPARISON
    # -----------------------------
    st.subheader("📊 Model Comparison")
    acc_df = pd.DataFrame({
        "Model":["Logistic Regression","Decision Tree","Random Forest"],
        "Accuracy":[acc_lr,acc_dt,acc_rf]
    })
    st.dataframe(acc_df)
    st.bar_chart(acc_df.set_index("Model"))

    # -----------------------------
    # BEST MODEL
    # -----------------------------
    best_name = "Random Forest" if acc_rf >= acc_lr and acc_rf >= acc_dt else "Decision Tree" if acc_dt>=acc_lr else "Logistic Regression"
    best_pred = rf_pred if best_name=="Random Forest" else dt_pred if best_name=="Decision Tree" else lr_pred

    st.success(f"🏆 Best Model: {best_name}")
    st.info(f"Accuracy: {round(max(acc_lr, acc_dt, acc_rf)*100,2)}%")

    # -----------------------------
    # CONFUSION MATRIX
    # -----------------------------
    st.subheader("🧩 Confusion Matrix")
    labels = ["Poor","Average","Good","Excellent"]
    cm = confusion_matrix(y_test, best_pred, labels=labels)
    fig, ax = plt.subplots()
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=labels, yticklabels=labels, ax=ax)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    st.pyplot(fig)

    # -----------------------------
    # PERFORMANCE DISTRIBUTION
    # -----------------------------
    st.subheader("📊 Performance Distribution")
    perf_counts = model_data["Performance"].value_counts()
    col1,col2,col3,col4 = st.columns(4)
    col1.metric("🟢 Excellent",perf_counts.get("Excellent",0))
    col2.metric("🔵 Good",perf_counts.get("Good",0))
    col3.metric("🟡 Average",perf_counts.get("Average",0))
    col4.metric("🔴 Poor",perf_counts.get("Poor",0))

    # -----------------------------
    # RISK STUDENTS
    # -----------------------------
    st.subheader("⚠️ Risk Students (Poor Performance)")
    risk_students = model_data[model_data["Performance"]=="Poor"]
    st.markdown(f"**Number of Risk Students: {len(risk_students)}**")
    if not risk_students.empty:
        st.dataframe(risk_students)
    else:
        st.info("No risk students found.")

    # -----------------------------
    # STUDENT FEEDBACK (Persistent per dataset)
    # -----------------------------
    st.subheader("💬 Student Feedback")
    uploaded_file_name = st.session_state.get("uploaded_file_name","default_dataset")
    feedback_file = f"feedback_{uploaded_file_name}.csv"

    # Load feedback CSV if exists
    if os.path.exists(feedback_file):
        feedback_df = pd.read_csv(feedback_file)
    else:
        feedback_df = pd.DataFrame(columns=["Student_ID", "Feedback"])

    if not feedback_df.empty:
        st.dataframe(feedback_df, use_container_width=True)

        st.download_button(
            label="📥 Download Feedback CSV",
            data=feedback_df.to_csv(index=False, encoding='utf-8'),
            file_name=f"student_feedback_{uploaded_file_name}.csv",
            mime="text/csv"
        )
    else:
        st.info("No feedback submitted for this dataset yet.")