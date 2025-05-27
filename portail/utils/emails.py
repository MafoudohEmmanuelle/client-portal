from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse
from django.core.mail import send_mail

def envoyer_email_notification(sujet, message, destinataires):
    send_mail(
        subject=sujet,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=destinataires,
        fail_silently=False,
    )

def send_activation_email(user, request):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    activation_link = request.build_absolute_uri(
        reverse('set_password', kwargs={'uidb64': uid, 'token': token})
    )
    subject = f"Activation de votre compte"

    try:
        send_mail(
            subject=subject,
            message=f"Bonjour,\n\nVeuillez définir votre mot de passe en cliquant sur ce lien : {activation_link}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False  
        )
        print(f"[ACTIVATION EMAIL] Envoyé à {user.email}")
    except Exception as e:
        print(f"[ERREUR EMAIL] Impossible d’envoyer le mail d’activation : {e}")

"""
def resend_client_invitation(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    user = client.utilisateur

    if user.is_active:
        messages.info(request, "Ce client a déjà activé son compte.")
        return redirect('client_list')

    send_activation_email(user, request)
    messages.success(request, "Nouvelle invitation envoyée.")
    return redirect('client_list')
"""