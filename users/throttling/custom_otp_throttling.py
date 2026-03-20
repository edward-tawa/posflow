from django.core.cache import cache
from rest_framework.throttling import BaseThrottle



class OtpThrottle(BaseThrottle):
    """
    Custom throttle class to limit OTP requests.
    """
    MAX_COUNT = 5
    MAX_TIME = 60 

    def allow_request(self, request, view):
        user_ip = request.META.get('REMOTE_ADDR')
        cache_key = f'otp_throttle_{user_ip}'
        request_count = cache.get(cache_key, 0)

        if request_count >= self.MAX_COUNT:
            return False
        
        cache.set(cache_key, request_count + 1, timeout=self.MAX_TIME)
        return True


class OtpVerificationThrottle(BaseThrottle):
    """
    Custom throttle class to limit OTP verification attempts.
    """
    MAX_COUNT = 5
    MAX_TIME = 60

    def allow-request(self, request, view):