#!/usr/bin/env python
import os
import sys
import django


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "demo.settings")
    django.setup()

    from model_creator.logic import register_models_from_templates
    register_models_from_templates()

    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
