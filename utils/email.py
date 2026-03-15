import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

API_URL = os.getenv("API_URL", "http://localhost:8000")


def send_verification_email(email: str, token: str):

    verify_link = f"{API_URL}/auth/verify-email?token={token}"

    subject = "Verify your email"

    text_body = f"""
Hello,

Please click the link below to verify your email:

{verify_link}

If you did not create this account, ignore this email.
"""

    html_body = f"""
<html>
<body>
<h3>Email Verification</h3>

<p>Please click the button below to verify your email:</p>

<a href="{verify_link}"
style="
padding:10px 20px;
background:#4CAF50;
color:white;
text-decoration:none;
border-radius:5px;
">
Verify Email
</a>

<p>If you did not create this account, ignore this email.</p>

</body>
</html>
"""

    message = MIMEMultipart("alternative")

    message["From"] = SMTP_USER
    message["To"] = email
    message["Subject"] = subject

    message.attach(MIMEText(text_body, "plain"))
    message.attach(MIMEText(html_body, "html"))

    try:

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:

            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)

            server.sendmail(
                SMTP_USER,
                email,
                message.as_string()
            )

    except Exception as e:

        print("Email sending failed:", e)