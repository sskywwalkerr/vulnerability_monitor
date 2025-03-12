import smtplib

from pydantic import EmailStr

from api.config import Config
from api.tasks.celery import celery
from api.tasks.email_templates import create_booking_confirmation_template


@celery.task
def send_booking_confirmation_email(
    booking: dict,
    email_to: EmailStr
):
    email_to_user = Config.MAIL_USERNAME
    email_content = create_booking_confirmation_template(
        booking=booking, email_to=email_to_user
    )
    try:
        with smtplib.SMTP_SSL(Config.MAIL_SERVER, Config.MAIL_PORT) as server:
            server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
            server.send_message(email_content)
        print("Email sent successfully")
    except Exception as e:
        print(f"Error sending email: {e}")
        raise
