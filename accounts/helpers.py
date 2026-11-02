from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse

def send_confirmation_email(token, request=None):
    confirmation_path = reverse('confirm_email', args=[token.token])
    if request is not None:
        link = request.build_absolute_uri(confirmation_path)
    else:
        link = f"{settings.SITE_URL.rstrip('/')}{confirmation_path}"
    send_mail(
        subject="Подтвердите адрес электронной почты",
        message=f"Подтвердите адрес электронной почты: {link}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[token.user.email],
    )



