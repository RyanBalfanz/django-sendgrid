import django.dispatch

sendgrid_email_sent = django.dispatch.Signal(providing_args=["response"])
# sendgrid_email_sent = django.dispatch.Signal(providing_args=["sender", "instance", "response"])
