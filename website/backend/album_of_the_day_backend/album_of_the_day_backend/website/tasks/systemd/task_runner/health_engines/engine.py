"""template.py
Defines a health engine template class that can be derived from."""
import logging
from typing import Dict


class HealthEngine:
    def __init__(self, config: Dict):
        """Initializes a health engine.

        :param config: The configuration of the task runner. See task_runner.py."""
        self.config = config
        self.logger = logging.getLogger(__name__)  # Set up a little logger.
        # Note: self.engine_name will be set on class children specifying what the current engine is.

    def get_engine_config(self) -> Dict:
        """Gets config related to the currently active engine."""
        try:
            return self.config[self.engine_name]
        except KeyError as e:
            raise KeyError(
                f"Missing health engine config entry: {self.engine_name} must exist in your configuration file."
            )
