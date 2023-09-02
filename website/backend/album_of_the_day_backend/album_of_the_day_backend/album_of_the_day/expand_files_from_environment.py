"""expand_files_from_environment.py
When using the Dockerfile with for example a CI/CD-tool,
you can store the content of secret files (wallet files for Oracle Cloud)
and configuration files inside environment variables.
This script expands the content of those variables - which should be the
file contents Base64-encoded (using the base64 Linux CLI as a baseline).
Note that environment variables will not be expanded to files if the target file
already exists.
Also note that this script does pretty much the same as the expand-environment-files.sh script in the
github_actions_scripts folder.
This script is run by a Dockerfile and should be run with the working directory being the same as the location
of this file (os.dirname(__file__))."""
import os, logging, base64, dotenv

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
if "album_of_the_day_backend" in os.listdir(os.getcwd()):
    os.chdir(
        os.path.join(os.getcwd(), "album_of_the_day_backend")
    )  # cd into correct directory
FILES_TO_EXPAND = [  # Format: (<file name>, <environment variable name>)
    (".wallet/cwallet.sso", "ORACLE_WALLET_FILE_CONTENTS"),
    (".wallet/sqlnet.ora", "ORACLE_SQLNET_FILE_CONTENTS"),
    (".wallet/tnsnames.ora", "ORACLE_TNSNAMES_FILE_CONTENTS"),
    (
        "website/tasks/systemd/task_runner/config.toml",
        "TASK_RUNNER_CONFIG_FILE_CONTENTS",
    ),
]


def expand_files() -> None:
    """Expands files from environment variables with Base64-encoded data of the file, if they are set."""
    if bool(
        os.environ.get("EXPAND_FILES_FROM_ENVIRONMENT", True)
    ):  # Can be used to control behaviour
        for file_to_expand, environment_variable_to_use in FILES_TO_EXPAND:
            if os.path.exists(file_to_expand):
                logger.info(
                    f"Not expanding {file_to_expand}: already exists on target filesystem."
                )
            else:
                variable_value = os.environ.get(environment_variable_to_use, None)
                if variable_value is not None:
                    logger.info(
                        f"Expanding Base64 encoded environment variable {environment_variable_to_use}..."
                    )
                    logger.info(f"(variable length: {len(variable_value)})")
                    parent_directory = os.path.dirname(file_to_expand)
                    if not os.path.exists(parent_directory):
                        logger.info(f"Creating directory {parent_directory}...")
                        os.makedirs(parent_directory)
                        logger.info(f"Directory {parent_directory} created.")
                    with open(file_to_expand, "wb") as new_file:
                        new_file.write(base64.b64decode(variable_value))
                        new_file.flush()
                        new_file.seek(0)
                    if len(open(file_to_expand, "r").read()) == 0:
                        error_message = f"New contents of {file_to_expand} is 0. Please check your environment variables!"
                        logger.critical(error_message)
                        raise ValueError(error_message)
                    logger.info("File expanded.")
                else:
                    raise FileNotFoundError(
                        f"Missing file {file_to_expand} in file system, and no corresponding environment variable is defined for it!"
                    )


if __name__ == "__main__":
    expand_files()
