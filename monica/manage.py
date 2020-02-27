#!/usr/bin/env python3
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shared.settings.appglobalconf")
    try:
        
        from django.core.management import execute_from_command_line

        # IF --noreload is enabled
        # import ptvsd

        # ptvsd.enable_attach("my_secret", address=('0.0.0.0', 3000))

    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
