from django.dispatch import Signal

# signal sent when an impersonation session begins
session_begin = Signal()

# signal sent when an impersonation session ends
session_end = Signal()
