import streamlit as st
from email_utils import send_email
from db_connection import get_connection

# Page configuration
st.set_page_config(
    page_title="Guard Portal",
    page_icon="📦",
    layout="centered"
)

st.title("📦 Guard Portal - Parcel Management System")

# ============================================================
# Session State
# ============================================================
if "guard_logged_in" not in st.session_state:
    st.session_state.guard_logged_in = False

if "guard_username" not in st.session_state:
    st.session_state.guard_username = ""


# ============================================================
# Database Connection
# ============================================================
conn = get_connection()
cursor = conn.cursor()

try:
    # ========================================================
    # GUARD LOGIN
    # ========================================================
    if not st.session_state.guard_logged_in:
        st.subheader("Guard Login")

        username = st.text_input(
            "Username",
            key="guard_login_username"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="guard_login_password"
        )

        if st.button("Login", key="guard_login_button"):
            cursor.execute(
                """
                SELECT *
                FROM guards
                WHERE username=%s AND password=%s
                """,
                (username, password)
            )

            guard = cursor.fetchone()

            if guard:
                st.session_state.guard_logged_in = True
                st.session_state.guard_username = username
                st.rerun()
            else:
                st.error("Invalid Username or Password")

    # ========================================================
    # GUARD DASHBOARD
    # ========================================================
    else:
        col_title, col_logout = st.columns([3, 1])

        with col_title:
            st.success(
                f"Welcome, {st.session_state.guard_username}"
            )

        with col_logout:
            if st.button("Logout", key="guard_logout_button"):
                st.session_state.guard_logged_in = False
                st.session_state.guard_username = ""
                st.rerun()

        st.subheader("📋 Expected Parcels")

        # ----------------------------------------------------
        # Get ALL expected parcels.
        #
        # IMPORTANT:
        # We never delete rows from expected_parcels.
        # Received status is calculated from the parcels table.
        # ----------------------------------------------------
        cursor.execute(
            """
            SELECT
                student_id,
                student_name,
                order_id,
                expected_delivery_date,
                product_category
            FROM expected_parcels
            ORDER BY student_name, order_id
            """
        )

        expected = cursor.fetchall()

        if expected:
            # ------------------------------------------------
            # Get received student/order combinations.
            # ------------------------------------------------
            cursor.execute(
                """
                SELECT student_id, order_id
                FROM parcels
                """
            )

            received_rows = cursor.fetchall()

            received_keys = {
                (str(row[0]), str(row[1]))
                for row in received_rows
            }

            # ------------------------------------------------
            # Build display data with Pending / Received status.
            # ------------------------------------------------
            display_rows = []

            for row in expected:
                student_id = row[0]
                student_name = row[1] or ""
                order_id = row[2]
                expected_date = row[3]
                category = row[4]

                key = (str(student_id), str(order_id))

                status = (
                    "Received"
                    if key in received_keys
                    else "Pending"
                )

                display_rows.append(
                    {
                        "Student ID": student_id,
                        "Student Name": student_name,
                        "Order ID": order_id,
                        "Expected Delivery": expected_date,
                        "Category": category,
                        "Status": status
                    }
                )

            # ------------------------------------------------
            # Display ALL parcels.
            # ------------------------------------------------
            st.dataframe(
                display_rows,
                use_container_width=True,
                hide_index=True
            )

            # =================================================
            # RECEIVE PARCEL
            # =================================================
            st.subheader("Receive Parcel")

            search = st.text_input(
                "Search Student Name, Student ID, or Order ID",
                key="parcel_search"
            )

            search_value = search.strip().lower()

            if search_value:
                filtered = [
                    row
                    for row in expected
                    if (
                        search_value in str(row[0]).lower()
                        or search_value in str(row[1] or "").lower()
                        or search_value in str(row[2]).lower()
                    )
                ]
            else:
                filtered = expected

            if filtered:
                selected = st.selectbox(
                    "Select Student / Parcel",
                    filtered,
                    format_func=lambda row: (
                        f"{row[1] or 'Unknown'} "
                        f"({row[0]}) - Order: {row[2]}"
                    ),
                    key="selected_parcel"
                )

                student_id = selected[0]
                student_name = selected[1] or ""
                order_id = selected[2]

                selected_key = (
                    str(student_id),
                    str(order_id)
                )

                already_received = (
                    selected_key in received_keys
                )

                st.text_input(
                    "Student Name",
                    value=student_name,
                    disabled=True,
                    key="receive_student_name"
                )

                st.text_input(
                    "Student ID",
                    value=str(student_id),
                    disabled=True,
                    key="receive_student_id"
                )

                st.text_input(
                    "Order ID",
                    value=str(order_id),
                    disabled=True,
                    key="receive_order_id"
                )

                # --------------------------------------------
                # Already received: do not allow duplicate
                # receiving.
                # --------------------------------------------
                if already_received:
                    st.success(
                        "This parcel has already been received."
                    )

                else:
                    sticker_no = st.text_input(
                        "Sticker Number*",
                        key="receive_sticker_no"
                    )

                    courier_partner = st.selectbox(
                        "Courier Partner",
                        [
                            "Amazon",
                            "Flipkart",
                            "Delhivery",
                            "Blue Dart",
                            "DTDC",
                            "Ekart",
                            "India Post",
                            "Other"
                        ],
                        key="receive_courier"
                    )

                    received_date = st.date_input(
                        "Received Date",
                        key="receive_date"
                    )

                    received_time = st.time_input(
                        "Received Time",
                        key="receive_time"
                    )

                    if st.button(
                        "Parcel Received",
                        key="parcel_received_button"
                    ):
                        sticker_no = sticker_no.strip()

                        if not sticker_no:
                            st.error(
                                "Please enter a valid Sticker Number."
                            )
                        else:
                            try:
                                # --------------------------------
                                # Insert into parcels.
                                # --------------------------------
                                cursor.execute(
                                    """
                                    INSERT INTO parcels
                                    (
                                        student_id,
                                        order_id,
                                        sticker_no,
                                        courier_partner,
                                        received_date,
                                        received_time,
                                        name
                                    )
                                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                                    """,
                                    (
                                        student_id,
                                        order_id,
                                        sticker_no,
                                        courier_partner,
                                        received_date,
                                        received_time,
                                        student_name
                                    )
                                )

                                # --------------------------------
                                # IMPORTANT:
                                # Do NOT delete from
                                # expected_parcels.
                                #
                                # This keeps the student/parcel
                                # permanently visible in the
                                # Expected Parcels list.
                                # --------------------------------
                                conn.commit()

                                # --------------------------------
                                # Look up email if available.
                                # Email is optional.
                                # --------------------------------
                                cursor.execute(
                                    """
                                    SELECT email
                                    FROM students
                                    WHERE student_id=%s
                                    """,
                                    (student_id,)
                                )

                                student_record = cursor.fetchone()

                                email_sent = False

                                if (
                                    student_record
                                    and student_record[0]
                                ):
                                    try:
                                        send_email(
                                            student_record[0],
                                            student_id,
                                            order_id,
                                            sticker_no,
                                            received_date
                                        )
                                        email_sent = True
                                    except Exception:
                                        email_sent = False

                                if email_sent:
                                    st.success(
                                        "Parcel recorded successfully "
                                        "and email sent!"
                                    )
                                else:
                                    st.success(
                                        "Parcel recorded successfully!"
                                    )

                                st.rerun()

                            except Exception as e:
                                conn.rollback()
                                st.error(
                                    f"Could not record parcel: {e}"
                                )

            else:
                # Informational only; not a student/profile error.
                st.info(
                    "No parcel matches your search."
                )

        else:
            st.info("No expected parcels found.")

finally:
    try:
        cursor.close()
    except Exception:
        pass

    try:
        conn.close()
    except Exception:
        pass
