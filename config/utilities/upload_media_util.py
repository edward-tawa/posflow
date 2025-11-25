import os

def upload_to_app_folder(instance, filename):
    # Automatically store media inside the app's folder based on the model's app label
    app_label = instance._meta.app_label
    model_name = instance.__class__.__name__.lower()
    return os.path.join(app_label, model_name, filename)
