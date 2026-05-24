import logging
import smtplib
from email.message import EmailMessage

from src.conf.config import settings

logger = logging.getLogger(__name__)


def send_verification_email(email: str, username: str, token: str) -> None:
    if not settings.MAIL_USERNAME or not settings.MAIL_PASSWORD or not settings.MAIL_FROM:
        logger.warning("Skipping verification email because mail settings are incomplete")
        return

    verify_url = f"{settings.FRONTEND_BASE_URL.rstrip('/')}/verify-email?token={token}"

    message = EmailMessage()
    message["Subject"] = "Verify your email"
    message["From"] = settings.MAIL_FROM
    message["To"] = email
    message.set_content(
        "\n".join(
            [
                f"Hello, {username}!",
                "",
                "Please verify your email by following the link below:",
                verify_url,
            ]
        )
    )

    with smtplib.SMTP(settings.MAIL_SERVER, settings.MAIL_PORT) as server:
        if settings.MAIL_STARTTLS:
            server.starttls()
        server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
        server.send_message(message)