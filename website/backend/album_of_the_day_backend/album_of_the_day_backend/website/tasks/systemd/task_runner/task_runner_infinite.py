"""task_runner_infinite.py
This is a hacky way of running tasks together with a Django application
running inside the same virtual machine. This task runner uses the config.toml
and the task_runner.py to calculate the next task to be run, and runs it.
Simple as that, but still a little bit unclean."""
import datetime
import random
import time
from threading import Thread
from task_runner import run, get_config
import pytz
from cron_converter import Cron
import logging

# Create logger
logger = logging.getLogger(__name__)
# Get config
CONFIG = get_config()
# Get all tasks
TASKS_CONFIG = CONFIG["tasks"]
TASK_TIMINGS = TASKS_CONFIG["timings"]
upcoming_runs = {}  # Stores the upcoming runs for each tasks
if len(TASK_TIMINGS) > 0:
    logger.info(f"Starting infinite task runner with {len(TASK_TIMINGS)} tasks.")
    while True:
        # Spawn the tasks accordingly
        for task_name, task_information in TASK_TIMINGS.items():
            # Get the task crontab
            task_crontab = task_information["crontab"]
            task_crontab_parsed = Cron(task_crontab)
            # Get a time reference for when to check the next schedule
            task_time_reference = datetime.datetime.now(
                tz=pytz.timezone("Europe/Stockholm")
            )
            task_crontab_schedule = task_crontab_parsed.schedule(task_time_reference)
            next_run = task_crontab_schedule.next()
            # Store the next run if needed
            next_run_stored = upcoming_runs.get(task_name, None)
            if next_run_stored != next_run:
                if next_run_stored is not None:
                    # Run the task inside a thread
                    logger.info(f"Running the task {task_name}...")
                    task_thread = Thread(target=run, kwargs={"task_name": task_name})
                    task_thread.start()
                    logger.info(f"Thread for {task_name} was started.")
                upcoming_runs[task_name] = next_run
                logger.info(f"Queued: {task_name} is queued to run on {next_run}.")
        time.sleep(5)  # Wait 5 seconds until the next check
raise ValueError("No tasks set up to run! The task runner will not start.")
