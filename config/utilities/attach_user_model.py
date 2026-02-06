
def attach_user_to_model(request, instance):
    """
    Attach the currently logged-in user to a model instance
    so signals can pick it up.
    """
    instance._user = getattr(request, "user", None)
    return instance
