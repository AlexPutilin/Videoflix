from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


def send_activation_email(user, token):
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    activation_url = f"{settings.FRONTEND_URL}/pages/auth/activate.html?uid={uidb64}&token={token}"
    context = {
        "user": user,
        "activation_url": activation_url,
    }
    send_templated_email(
        "activation_email",
        "Confirm your email",
        user.email,
        context
    )


def send_password_reset_email(user):
    token = default_token_generator.make_token(user)
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    reset_url = f"{settings.FRONTEND_URL}/pages/auth/confirm_password.html?uid={uidb64}&token={token}"
    context = {
        "reset_url": reset_url,
    }
    send_templated_email(
        "password_reset_email",
        "Reset your password",
        user.email,
        context,
    )


def send_templated_email(template_name, subject, recipient, context):
    text_path = f"app_auth/emails/{template_name}.txt"
    html_path = f"app_auth/emails/{template_name}.html"
    message = render_to_string(text_path, context)
    html_message = render_to_string(html_path, context)
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient],
        html_message=html_message,
        fail_silently=False,
    )