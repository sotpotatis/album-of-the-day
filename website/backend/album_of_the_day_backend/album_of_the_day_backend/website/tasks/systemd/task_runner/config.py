"""config.py
Handles loading of task runner configuration file."""
import os, toml
from typing import Dict

# Config is by default located in the same directory as the task runner
SCRIPT_PATH = os.path.realpath(__name__)
TASK_RUNNER_PATH = os.path.dirname(SCRIPT_PATH)
CONFIGURATION_PATH = os.environ.get(
    "TASK_RUNNER_CONFIGURATION_PATH", os.path.join(TASK_RUNNER_PATH, "config.toml")
)


def get_config() -> Dict:
    """Reads and returns the config."""
    return toml.loads(open(CONFIGURATION_PATH, "r").read())


def update_config(new_config: Dict) -> None:
    """Updates the current configuration.

    :param new_config: The new configuration to write."""
    with open(CONFIGURATION_PATH, "w", encoding="UTF-8") as configuration_file:
        configuration_file.write(toml.dumps(new_config))
