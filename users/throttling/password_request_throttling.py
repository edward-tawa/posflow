from rest_framework.throttling import AnonRateThrottle



class PasswordResetRequestThrottle(AnonRateThrottle):
    scope = "password_reset_request"  # max 5 requests per minute per IP