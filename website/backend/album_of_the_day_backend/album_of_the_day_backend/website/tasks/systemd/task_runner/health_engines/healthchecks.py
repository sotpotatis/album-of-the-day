"""healthchecks.py
Healthchecks health engine."""
import warnings

from .engine import HealthEngine
from . import HEALTH_ENGINE_HEALTHCHECKS, TASK_STATUS, TASK_STATE, HealthEngineError
from typing import Dict, Optional
import requests


class HealthchecksHealthEngine(HealthEngine):
    def __init__(self, *args, **kwargs):
        self.engine_name = HEALTH_ENGINE_HEALTHCHECKS
        super().__init__(*args, **kwargs)

    def send_status(
        self,
        task_name: str,
        task_state: TASK_STATE,
        task_status: Optional[TASK_STATUS] = None,
    ) -> None:
        """Sends status for a specific task to Healthchecks.

        :param task_name: The name of the task.

        :param task_status: The output/result of the task."""
        config = self.get_engine_config()
        if not task_name in config:
            raise KeyError(
                f"Missing configuration for task {task_name} in Healthchecks config. It is mandatory."
            )
        try:
            # Build a URL
            request_url = config.get("base_url", "https://hc-ping.com").strip("/")
            request_url += f"/{config[task_name]['uuid']}"
            if task_state == TASK_STATE.STARTING:
                request_url += "/start"
            elif task_status == TASK_STATUS.FAILURE:
                request_url += "/fail"
            # (note: for TASK_STATUS.SUCCESS, you simply send the UUID, which is
            # the URL as it looks like before entering this if checking scenadigan thingy)
            self.logger.info(f"Built request URL for Healthchecks: {request_url}.")
            request = requests.get(
                request_url,
                headers={
                    "User-Agent": "Python/AlbumOfTheDayTaskRunnerHealthEngine"  # Loved spelling that out!
                },
            )
            if request.status_code not in [200, 204]:
                raise HealthEngineError(
                    f"An unexpected status code was returned from Healthchecks: {request.status_code}. It's unsure whether the ping was successful or not."
                )
            else:
                self.logger.info(
                    f"Ping message sent to Healthchecks with status code {request.status_code}."
                )
        except Exception as e:
            self.logger.warning(
                f"Failed to send health engine status due to an error! ({e}) It is possible that the status was not reported properly.",
                exc_info=True,
            )
