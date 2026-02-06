from django.core.management.base import BaseCommand
from django.apps import apps
from pathlib import Path


SCHEMA_DIR = Path("domain/schemas")


class Command(BaseCommand):
    help = "Auto-generate Pydantic schemas from Django models"

    def handle(self, *args, **options):
        SCHEMA_DIR.mkdir(parents=True, exist_ok=True)

        app_model_map = {}

        for model in apps.get_models():
            app_label = model._meta.app_label
            model_name = model.__name__

            # Skip Django internal apps
            if app_label in {"admin", "auth", "contenttypes", "sessions"}:
                continue

            app_model_map.setdefault(app_label, []).append(model_name)

        for app_label, models in app_model_map.items():
            file_path = SCHEMA_DIR / f"{app_label}.py"

            with open(file_path, "w") as f:
                f.write("from drf_pydantic import ModelSchema\n")
                f.write(f"from {app_label}.models import {', '.join(models)}\n\n")

                for model in models:
                    f.write(f"class {model}Schema(ModelSchema):\n")
                    f.write("    class Config:\n")
                    f.write(f"        model = {model}\n\n")

            self.stdout.write(self.style.SUCCESS(
                f"Generated schemas for app: {app_label}"
            ))
