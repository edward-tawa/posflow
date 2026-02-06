from django.core.management.base import BaseCommand
from pathlib import Path

SCHEMA_DIR = Path("core/schemas")
OUTPUT_FILE = SCHEMA_DIR / "all_schemas.py"

class Command(BaseCommand):
    help = "Merge all schema files into a single file"

    def handle(self, *args, **options):
        imports_seen = set()
        merged_lines = []

        for schema_file in sorted(SCHEMA_DIR.glob("*.py")):
            if schema_file.name == "__init__.py" or schema_file.name == "base.py":
                continue

            with open(schema_file) as f:
                for line in f:
                    stripped = line.strip()
                    # Collect import lines uniquely
                    if stripped.startswith("from") or stripped.startswith("import"):
                        if stripped not in imports_seen:
                            imports_seen.add(stripped)
                            merged_lines.append(line)
                    else:
                        merged_lines.append(line)

            merged_lines.append("\n\n")

        # Write to output file
        OUTPUT_FILE.write_text("".join(merged_lines))
        self.stdout.write(self.style.SUCCESS(
            f"Merged schemas into {OUTPUT_FILE}"
        ))
