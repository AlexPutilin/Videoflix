from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from email.message import MIMEPart
from pathlib import Path


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
    text_path = f"emails/{template_name}.txt"
    html_path = f"emails/{template_name}.html"
    context["logo_cid"] = "videoflix_logo"
    message = render_to_string(text_path, context)
    html_message = render_to_string(html_path, context)
    email = EmailMultiAlternatives(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient]
    )
    email.attach_alternative(html_message, "text/html")
    attach_inline_image(email)
    email.send(fail_silently=False)


def attach_inline_image(email):
    image_path = (Path(settings.BASE_DIR) / "app_auth/static/images/logo.png")
    if not image_path.exists():
        return
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()
    inline_image = MIMEPart()
    inline_image.set_content(
        image_data,
        maintype="image",
        subtype="png",
        disposition="inline",
        cid="<videoflix_logo>",
    )
    email.attach(inline_image)