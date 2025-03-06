from celery import Celery
from api.mail import mail, create_message
from asgiref.sync import async_to_sync

c_app = Celery()

c_app.config_from_object("api.config")


@c_app.task()
def send_email(recipients: list[str], subject: str, body: str):
    print(f"Sending email to: {recipients}, subject: {subject}")
    try:
        message = create_message(recipients=recipients, subject=subject, body=body)
        async_to_sync(mail.send_message)(message)
        print("Email sent")
    except Exception as e:
        print(f"Error sending email: {e}")
