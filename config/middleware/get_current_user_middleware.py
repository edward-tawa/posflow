import threading

# Middleware
_thread_locals = threading.local()

class CurrentUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.current_user = getattr(request, "user", None)
        response = self.get_response(request)
        _thread_locals.current_user = None
        return response

def get_current_user():
    return getattr(_thread_locals, "current_user", None)
