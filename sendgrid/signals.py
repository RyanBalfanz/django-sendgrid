import django.dispatch

sendgrid_email_sent = django.dispatch.Signal(providing_args=["response", "message"])
post_send = sendgrid_email_sent
sendgrid_event_recieved = django.dispatch.Signal()
