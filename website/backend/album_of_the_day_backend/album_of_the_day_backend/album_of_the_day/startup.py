"""startup.py
Runs startup tasks - spawns long-running threads that are connected
to the website."""
import logging, sys
import os
from threading import Thread
from typing import List, Tuple, Callable

# Set up logging
logger = logging.getLogger(__name__)
FILE_PATH = os.path.realpath(__file__)  # Get path of current file
PARENT_DIRECTORY = os.path.dirname(FILE_PATH)  # Get parent directory
ROOT_DIRECTORY = os.path.dirname(
    PARENT_DIRECTORY
)  # Get the path of the root code for the website and other apps
os.environ["DJANGO_SETTINGS_MODULE"] = "../../album_of_the_day.settings"
os.environ.setdefault(
    os.environ["DJANGO_SETTINGS_MODULE"], os.environ["DJANGO_SETTINGS_MODULE"]
)
os.environ["DJANGO_SETTINGS_MODULE_ALREADY_SET"] = "True"


# Define tasks
def start_discord_bot():
    """Runs the Discord bot that is used by the backend to create new album of the day
    images."""
    logger.info("Starting Discord bot...")
    os.chdir(os.path.join(ROOT_DIRECTORY, "website/discord_bot"))
    sys.path.append(os.getcwd())
    import main


def run_task_runner():
    """Starts the task runner, which is handles some cronjobs like updating album covers,
    daily rotations, genre descriptions and Spotify UIDs."""
    logger.info("Starting task runner...")
    os.chdir(os.path.join(ROOT_DIRECTORY, "website/tasks/systemd/task_runner"))
    sys.path.append(os.getcwd())
    import task_runner_infinite


# List of tasks to run and a readable name for them
TASKS_TO_RUN: List[Tuple[Callable, str]] = [
    (start_discord_bot, "Discord bot"),
    (run_task_runner, "Task runner"),
]


def run_startup_tasks():
    """Runs all the defined startup tasks by spawing them in threads."""
    # Start all tasks in threads
    for task_to_run, name_of_task in TASKS_TO_RUN:
        logger.info(f"Starting a thread for {name_of_task}...")
        thread = Thread(target=task_to_run)
        thread.daemon = True
        thread.start()
        logger.info(f"Thread for {name_of_task} was started.")
