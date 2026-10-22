import streamlit as st
import mysql.connector

# ---------------- DATABASE CONNECTION ----------------

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Prayas@9658",
    database="parcel_db"
)

cursor = conn.cursor()

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="Student Portal",
    page_icon="📦",
    layout="centered"
)

st.title("📦 Student Parcel Management System")

# ---------------- SESSION ----------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "student_id" not in st.session_state:
    st.session_state.student_id = ""

# ---------------- LOGIN ----------------

if not st.session_state.logged_in:

    st.subheader("Student Login")

    student_id = st.text_input("Student ID")

    email = st.text_input("Email")

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Login"):

        cursor.execute(
            """
            SELECT *
            FROM students
            WHERE student_id=%s
            AND email=%s
            AND password=%s
            """,
            (
                student_id,
                email,
                password
            )
        )

        student = cursor.fetchone()

        if student:

            st.session_state.logged_in = True
            st.session_state.student_id = student_id

            st.success("✅ Login Successful")
            st.rerun()

        else:

            st.error("❌ Invalid Student Credentials")

# ---------------- AFTER LOGIN ----------------

else:

    st.success(
        f"Welcome Student {st.session_state.student_id}"
    )

    st.subheader("Enter Expected Parcel Details")

    student_name = st.text_input("Student Name", key="student_name")
    order_id = st.text_input("Order ID", key="order_id")
    

    expected_delivery_date = st.date_input(
        "Expected Delivery Date"
    )

    product_category = st.selectbox(
        "Product Category",
        [
            "Electronics",
            "Clothes",
            "Food",
            "Medicines",
            "Books",
            "Others"
        ]
    )

    if product_category == "Others":
        product_category = st.text_input(
            "Enter Product Description"
        )

    # ---------------- SUBMIT EXPECTED PARCEL ----------------

    if st.button("Submit Expected Parcel"):

        if order_id == "":
            st.warning("Please enter Order ID.")

        elif product_category == "":
            st.warning("Please enter Product Category.")

        else:

            # Check whether this Order ID already exists
            cursor.execute("""
                        SELECT student_id
                        FROM expected_parcels
                        WHERE order_id=%s
                        AND student_name=%s
""", (order_id, student_name))

# ---------------- ENTER EXPECTED PARCEL DETAILS ----------------

st.subheader("Enter Expected Parcel Details")

student_name = st.text_input("Student Name", key="student_name")
order_id = st.text_input("Order ID", key="order_id")

expected_delivery_date = st.date_input("Expected Delivery Date")

product_category = st.selectbox(
    "Product Category",
    [
        "Electronics",
        "Clothes",
        "Food",
        "Medicines",
        "Books",
        "Others"
    ]
)

if product_category == "Others":
    product_category = st.text_input("Enter Product Description")

# ---------------- SUBMIT EXPECTED PARCEL ----------------

if st.button("Submit Expected Parcel"):

    if student_name.strip() == "":
        st.warning("Please enter Student Name.")

    elif order_id.strip() == "":
        st.warning("Please enter Order ID.")

    elif product_category.strip() == "":
        st.warning("Please enter Product Category.")

    else:

        try:
            # Check whether Order ID already exists
            cursor.execute(
                """
                SELECT order_id
                FROM expected_parcels
                WHERE order_id=%s
                """,
                (order_id,)
            )

            existing = cursor.fetchone()

            if existing:
                st.warning("⚠️ This Order ID is already registered.")

            else:
                cursor.execute(
                    """
                    INSERT INTO expected_parcels
                    (
                        student_id,
                        order_id,
                        expected_delivery_date,
                        product_category,
                        student_name
                    )
                    VALUES (%s,%s,%s,%s,%s)
                    """,
                    (
                        st.session_state.student_id,
                        order_id,
                        expected_delivery_date,
                        product_category,
                        student_name
                    )
                )

                conn.commit()

                st.success("✅ Expected parcel registered successfully.")

        except mysql.connector.Error as err:
            st.error(f"Database Error: {err}")



        # ---------------- CHECK PARCEL STATUS ----------------

st.divider()

st.subheader("Check Parcel Status")

check_order_id = st.text_input(
        "Enter Order ID to Check Status"
    )

if st.button("Check Parcel Status"):

        if check_order_id == "":
            st.warning("Please enter Order ID.")

        else:

            cursor.execute(
                """
                SELECT
                    student_id,
                    order_id,
                    courier_partner,
                    sticker_no,
                    received_date,
                    received_time
                FROM parcels
                WHERE student_id=%s
                AND order_id=%s
                """,
                (
                    st.session_state.student_id,
                    check_order_id
                )
            )

            parcel = cursor.fetchone()

            if parcel:

                st.success("📦 Parcel Received Successfully!")

                st.write("### Parcel Details")

                st.write("**Student ID:**", parcel[0])
                st.write("**Order ID:**", parcel[1])
                st.write("**Courier Partner:**", parcel[2])
                st.write("**Sticker Number:**", parcel[3])
                st.write("**Received Date:**", parcel[4])
                st.write("**Received Time:**", parcel[5])

            else:

                st.info(
                    "Parcel has not been received yet."
                )

    # ---------------- LOGOUT ----------------

st.divider()

if st.button("Logout"):

        st.session_state.logged_in = False
        st.session_state.student_id = ""

        st.success("Logged out successfully.")

        st.rerun()

# ---------------- CLOSE DATABASE ----------------

cursor.close()
conn.close()

