import streamlit as st
from db_connection import get_connection

st.set_page_config(page_title="Student Portal", page_icon="📦")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "student_id" not in st.session_state:
    st.session_state.student_id = ""

def login_page():
    st.title("📦 Student Parcel Management System")
    st.subheader("Student Login")
    sid = st.text_input("Student ID", key="login_sid")
    email = st.text_input("Email", key="login_email")
    pwd = st.text_input("Password", type="password", key="login_pwd")
    if st.button("Login"):
        # TODO: Replace with MySQL verification
        if sid and email and pwd:
            st.session_state.logged_in = True
            st.session_state.student_id = sid
            st.rerun()
        else:
            st.error("Enter all login details.")

def dashboard():
    st.title("📦 Student Dashboard")
    st.success(f"Welcome {st.session_state.student_id}")
    st.subheader("Enter Expected Parcel Details")
    student_name = st.text_input("Student Name", key="student_name")
    order_id = st.text_input("Order ID", key="order_id")
    expected_delivery_date = st.date_input("Expected Delivery Date", key="edd")
    category = st.selectbox("Product Category",
                            ["Electronics","Clothes","Food","Medicines","Books","Others"],
                            key="category")
    if category=="Others":
        category = st.text_input("Enter Product Description", key="other")
    if st.button("Submit Expected Parcel"):
        try:
            conn=get_connection()
            cur=conn.cursor()
            cur.execute("""INSERT INTO expected_parcels (student_id,order_id,expected_delivery_date,product_category,student_name)
                        VALUES (%s,%s,%s,%s,%s)""",
                        (int(st.session_state.student_id),order_id,expected_delivery_date,category,student_name))
            conn.commit()
            st.success("Parcel details submitted.")
            cur.close()
            conn.close()
        except Exception as e:
            st.error(f"Database Error: {e}")
    st.divider()
    st.subheader("Check Parcel Status")
    chk = st.text_input("Enter Order ID", key="check")
    if st.button("Check Parcel Status"):
        st.info(f"Lookup parcel '{chk}' in your database.")
    st.divider()
    if st.button("Logout"):
        st.session_state.logged_in=False
        st.session_state.student_id=""
        st.rerun()

if not st.session_state.logged_in:
    login_page()
else:
    dashboard()
