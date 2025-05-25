from django.core.mail import send_mail
from django.conf import settings

def envoyer_email_notification(sujet, message, destinataires):
    send_mail(
        subject=sujet,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=destinataires,
        fail_silently=False,
    )
