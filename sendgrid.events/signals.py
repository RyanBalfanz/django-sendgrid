import django.dispatch

sendgrid_event_recieved = django.dispatch.Signal(providing_args=["event"])
