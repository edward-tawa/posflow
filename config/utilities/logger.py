# config/logging_config.py
from loguru import logger
import os
from django.conf import settings

def setup_loguru():
    """
    Dynamically sets up Loguru to create a separate log file per app
    inside the /logs directory.
    """
    log_dir = os.path.join(settings.BASE_DIR, "logs")
    os.makedirs(log_dir, exist_ok=True)

    # Remove any default Loguru handlers to avoid duplication
    logger.remove()

    # General project-level log file
    logger.add(
        os.path.join(log_dir, "posflow.log"),
        rotation="10 MB",
        retention="21 days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
        level="INFO",
    )

    # App-specific log files
    for app in settings.LOCAL_APPS:
        app_name = app.split(".")[-1]  # Just get the app name
        logger.add(
            os.path.join(log_dir, f"{app_name}.log"),
            rotation="5 MB",
            retention="21 days",
            compression="zip",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
            level="INFO",
            filter=lambda record, app_name=app_name: app_name in record["name"],  # only logs for that app
        )

    logger.info("Loguru logging initialized for all apps.")
    return logger
