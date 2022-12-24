from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail


def send_confirmation_mail(user):
    email = user.email
    confirmation_code = default_token_generator.make_token(user)
    subject = 'Регистрация на YAMDB'
    message = f'Код подтверждения: {confirmation_code}'
    send_mail(subject, message, 'YAMDB', [email])

    return confirmation_code
