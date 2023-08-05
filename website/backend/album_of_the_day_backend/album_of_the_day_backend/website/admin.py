from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.apps import apps
import logging

logger = logging.getLogger(__name__)
# Register your models here.
all_models = apps.get_models()
for model in all_models:
    logger.debug(f"Registering model: {model}")
    try:
        admin.site.register(model)  # We only want the model to be edited by the admin!
    except Exception as e:
        pass
