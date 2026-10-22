from datetime import timedelta
import smtplib
from email.mime.text import MIMEText

def send_email(receiver_email, student_id, order_id, sticker_no, received_date):

    sender_email = "prayasdas.210500@gmail.com"
    app_password = "rhnmcgjxhmqihcaa"

    collect_by = received_date + timedelta(days=2)

    subject = "Parcel Received - Collect from Guard Office"

    body = f"""
        Dear Student,

Your parcel has been received at the guard office.

Parcel Details:
• Student ID      : {student_id}
• Order ID        : {order_id}
• Sticker Number  : {sticker_no}
• Received Date   : {received_date}


Please collect your parcel on or before:
{collect_by.strftime("%m-%d-%Y")}

Kindly collect it within the mentioned collection date for smooth collection process.

Thank you.
GLIM-G
Guard Office
"""

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, app_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
