"""__init__.py
Defines some health engine related constants and mappings to find a requested
health engine."""
from typing import Dict
from .engine import HealthEngine

# Define some constants
HEALTH_ENGINE_HEALTHCHECKS = "healthchecks"
VALID_HEALTH_ENGINES = [HEALTH_ENGINE_HEALTHCHECKS]


# ... an exception...
class HealthEngineError(Exception):
    pass


# Task state: if the task is starting or finished.
class TASK_STATE:
    STARTING = "starting"
    FINISHED = "finished"


# Task statuses: how the task went if TASK_STATE is finished
class TASK_STATUS:
    SUCCESS = "success"
    FAILURE = "failure"


# Health engine mapping: type --> Health engine class
from .healthchecks import HealthchecksHealthEngine

HEALTH_ENGINES: Dict[str, HealthEngine] = {
    HEALTH_ENGINE_HEALTHCHECKS: HealthchecksHealthEngine
}
