import uuid
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings


def generate_verification_token():
    return str(uuid.uuid4())


def generate_password_token():
    return str(uuid.uuid4())


def send_forgot_password(user):
    token = user.forgot_password_token
    verification_url = reverse("password_reset_done", kwargs={"token": token})
    full_url = f"{settings.SITE_URL}{verification_url}"
    print(f"Verification URL: {full_url}")
    subject = "Reset Password"
    message = f"""
    Hi {user.get_full_name()}, 
    Click the link to verify your email and reset your password:
    {full_url}
    This link is valid for 5 minutes.
    """
    from_email = settings.DEFAULT_FROM_EMAIL
    send_mail(subject, message, from_email, [user.email])


def send_verification_email(user):
    # name = user.full_name[:2]
    token = user.email_verified_token
    verification_url = f"{settings.SITE_URL}/verify-email/?token={token}"
    subject = "Verify your email address"
    message = (
        f"hi {user.email}, click the link to verify your email: {verification_url}"
    )
    from_email = settings.DEFAULT_FROM_EMAIL
    send_mail(subject, message, from_email, [user.email])