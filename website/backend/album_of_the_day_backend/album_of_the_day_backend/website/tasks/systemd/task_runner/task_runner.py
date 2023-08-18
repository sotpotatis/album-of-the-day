"""task_runner.py
To simplify path handling and task tracking, I implemented a "task runner". See the README for more information."""
import logging, os, subprocess, sys
from config import get_config, update_config
from argparse import ArgumentParser
from health_engines import VALID_HEALTH_ENGINES, HEALTH_ENGINES, TASK_STATUS, TASK_STATE

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def run(task_name: str):
    """Starts the task runner and runs a set task.

    :param task_name: The name of the task to run."""
    # Load and parse config
    logger.info("Loading task runner config...")
    CONFIG = get_config()
    # Parse everything in the config
    try:
        # Set defaults
        DEFAULT_HEALTH_CONFIG = {"enabled": False, "engine": None}
        # Load sections
        BASIC_CONFIG = CONFIG["basics"]
        TASKS_DIRECTORY = os.path.abspath(BASIC_CONFIG["tasks_dir"])
        WEBSITE_DIRECTORY = os.path.abspath(
            BASIC_CONFIG.get(
                "website_directory", os.path.dirname(os.path.dirname(TASKS_DIRECTORY))
            )
        )
        # This (PYTHON_COMMAND_BASE) can be used to run scripts with a different prepended command than python.
        # For example, to run scripts as python3 <filename>, you can set it to "python3"
        PYTHON_COMMAND_BASE = BASIC_CONFIG.get("python_command", "python")
        HEALTH_CONFIG = CONFIG.get("health", DEFAULT_HEALTH_CONFIG)
        HEALTH_ENGINE = (
            None if not HEALTH_CONFIG["enabled"] else HEALTH_CONFIG["engine"]
        )
        if HEALTH_ENGINE is not None and HEALTH_ENGINE not in VALID_HEALTH_ENGINES:
            raise ValueError(
                f"Invalid health engine: must be one of: {','.join(VALID_HEALTH_ENGINES)}"
            )
    except KeyError as e:
        logger.critical(
            f"Failed to load task runner config: one or more parameters are mandatory, but not defined ({e}). Please set them up and try again.",
            exc_info=True,
        )
        exit(1)
    except ValueError as e:
        logger.critical(
            f"Something is improperly configured. Please see the error message: {e}",
            exc_info=True,
        )
        exit(1)
    # Initialize health engine
    REPORT_STATUS = HEALTH_ENGINE is not None
    if REPORT_STATUS:
        health_engine = HEALTH_ENGINES[HEALTH_ENGINE](CONFIG)
        logger.info("Health engine initialized.")
    # Add website directory to path
    sys.path.append(WEBSITE_DIRECTORY)
    # Try to find the task name
    logger.info("Looking for task name to run...")
    TASK_FILE = os.path.join(TASKS_DIRECTORY, f"{task_name}.py")
    if not os.path.exists(TASK_FILE):
        logger.critical(
            f"Can not find the requrested task name to run ({TASK_FILE} not found). Please check that the file exists and try again."
        )
        exit(1)
    # Report status if configured
    if REPORT_STATUS:
        logger.info("Reporting task start...")
        health_engine.send_status(task_name=TASK_NAME, task_state=TASK_STATE.STARTING)
    # Add website directory to path
    environment = os.environ.copy()
    if "PYTHONPATH" not in environment:
        environment["PYTHONPATH"] = ""
    environment["PYTHONPATH"] += WEBSITE_DIRECTORY
    if not bool(os.environ.get("DJANGO_SETTINGS_MODULE_ALREADY_SET", False)):
        environment["DJANGO_SETTINGS_MODULE"] = "album_of_the_day.settings"
        environment.setdefault("DJANGO_SETTINGS_MODULE", "album_of_the_day.settings")
    else:
        logger.info("Settings provided by user.")
    logger.info("Setting up Django environment...")
    logger.info(f"(Django settings module: {environment['DJANGO_SETTINGS_MODULE']})")
    # Set up Django environment
    import django

    django.setup()
    logger.debug(f"Created environment: {environment}")
    logger.info(f"Running the task {task_name}...")
    command = f"{PYTHON_COMMAND_BASE} {TASK_FILE}"
    return_code = subprocess.call(command, shell=True, env=environment)
    # Parse output
    task_failed = False
    if return_code != 0:
        logger.critical(f"Running task failed. Unexpected return code! ({return_code})")
        task_failed = True
    logger.info("Running task succeeded.")
    # Report status if configured
    if REPORT_STATUS:
        logger.info("Reporting task status...")
        health_engine.send_status(
            task_name=task_name,
            task_state=TASK_STATE.FINISHED,
            task_status=TASK_STATUS.SUCCESS if not task_failed else TASK_STATUS.FAILURE,
        )
        logger.info("Task status reported.")
    logger.info(f"Task run for {task_name} succeeded.")


if __name__ == "__main__":
    # Define CLI interface
    cli = ArgumentParser()
    cli.add_argument("task_name", type=str, help="The task that you want to run.")
    arguments = cli.parse_args()  # Parse arguments
    TASK_NAME = arguments.task_name
    run(TASK_NAME)
