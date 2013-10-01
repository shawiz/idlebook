from django.dispatch import Signal

email_confirmed = Signal(providing_args=["profile"])
email_confirmation_sent = Signal(providing_args=["email_confirmation"])
