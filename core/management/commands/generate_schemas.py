from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import models
from pathlib import Path


SCHEMA_DIR = Path("core/schemas")


TYPE_MAP = {
    models.CharField: "str",
    models.TextField: "str",
    models.EmailField: "str",
    models.URLField: "str",

    models.IntegerField: "int",
    models.BigIntegerField: "int",
    models.PositiveIntegerField: "int",
    models.PositiveBigIntegerField: "int",

    models.FloatField: "float",
    models.DecimalField: "Decimal",

    models.BooleanField: "bool",

    models.DateTimeField: "datetime",
    models.DateField: "date",

    models.UUIDField: "str",
    models.JSONField: "dict",
}


BASE_IMPORTS = """\
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Any
from core.schemas.base import Schema

"""


def django_field_to_type(field):
    # ForeignKey → *_id
    if isinstance(field, models.ForeignKey):
        return "int"

    # ManyToMany → list[int]
    if isinstance(field, models.ManyToManyField):
        return "list[int]"

    for django_type, py_type in TYPE_MAP.items():
        if isinstance(field, django_type):
            return py_type

    return "Any"


class Command(BaseCommand):
    help = "Generate explicit data-shape schemas for all Django models"

    def handle(self, *args, **options):
        SCHEMA_DIR.mkdir(parents=True, exist_ok=True)

        for app_config in apps.get_app_configs():
            app_label = app_config.label

            # Skip Django & third-party internals
            if app_label in {
                "admin", "auth", "contenttypes", "sessions",
                "messages", "staticfiles"
            }:
                continue

            models_in_app = list(app_config.get_models())
            if not models_in_app:
                continue

            file_path = SCHEMA_DIR / f"{app_label}.py"
            lines = [BASE_IMPORTS]

            for model in models_in_app:
                lines.append(self.generate_schema(model))
                lines.append("\n\n")

            file_path.write_text("".join(lines))

            self.stdout.write(self.style.SUCCESS(
                f"Generated schemas for app: {app_label}"
            ))

    def generate_schema(self, model):
        schema_name = f"{model.__name__}Schema"
        lines = [f"class {schema_name}(Schema):\n"]

        for field in model._meta.get_fields():
            # Skip reverse relations
            if field.auto_created and not field.concrete:
                continue

            field_name = field.name
            field_type = django_field_to_type(field)

            optional = getattr(field, "null", False) or getattr(field, "blank", False)
            py_type = f"Optional[{field_type}]" if optional else field_type

            lines.append(f"    {field_name}: {py_type}\n")

        if len(lines) == 1:
            lines.append("    pass\n")

        return "".join(lines)
