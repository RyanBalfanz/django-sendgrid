import django.dispatch

sendgrid_email_sent = django.dispatch.Signal(providing_args=["response", "message"])
sendgrid_event_recieved = django.dispatch.Signal(providing_args=["request"])
sendgrid_event_processed = django.dispatch.Signal(providing_args=["detail"])
