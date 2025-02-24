from email.message import EmailMessage

from pydantic import EmailStr

from api.config import Config


def create_booking_confirmation_template(
    booking: dict,
    email_to: EmailStr
):
    """Формирует email о подтверждении бронирования."""
    email = EmailMessage()

    email['Subject'] = 'Подтверждение бронирования.'
    email['From'] = Config.MAIL_USERNAME
    email['To'] = email_to

    confirmation_link = f"http://{Config.DOMAIN}/confirm_booking/{booking['uid']}"  # Ссылка для подтверждения

    email.set_content(
        f"""
        <h1>Подтвердите бронирование.</h1>
        Вы забронировали отель с {booking['date_from']} по {booking['date_to']}
        <a href="{confirmation_link}">Подтвердить бронирование</a>
        """,
        subtype='html'
    )
    return email
