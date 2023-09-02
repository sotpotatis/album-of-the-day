"""
ASGI config for album_of_the_day project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os, dotenv

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "album_of_the_day.settings")
# Load environment variables from backend.env in the working directory.
# Note: you can leave out this file, but it will most likely be defined because it is
# used in the Dockerfile.
dotenv.load_dotenv("./../.backend.env", verbose=True)
application = get_asgi_application()
