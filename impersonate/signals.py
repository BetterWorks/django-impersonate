from django.dispatch import Signal

# signal sent when an impersonation session begins
session_begin = Signal(
    providing_args=['impersonator', 'impersonating', 'request']
)

# signal sent when an impersonation session ends
session_end = Signal(
    providing_args=['impersonator', 'impersonating', 'request']
)
