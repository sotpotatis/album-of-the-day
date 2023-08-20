"""expand_files_from_environment.py
When using the Dockerfile with for example a CI/CD-tool,
you can store the content of secret files (wallet files for Oracle Cloud)
and configuration files inside environment variables.
This script expands the content of those variables - which should be the
file contents Base64-encoded (using the base64 Linux CLI as a baseline).
Note that environment variables will not be expanded to files if the target file
already exists.
Also note that this script does pretty much the same as the expand-environment-files.sh script in the
github_actions_scripts folder."""
import base64
import os, logging

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

FILES_TO_EXPAND = [  # Format: (<file name>, <environment variable name>)
    ("album_of_the_day_backend/.wallet/cwallet.sso", "ORACLE_WALLET_FILE_CONTENTS"),
    ("album_of_the_day_backend/.wallet/sqlnet.ora", "ORACLE_SQLNET_FILE_CONTENTS"),
    ("album_of_the_day_backend/.wallet/tnsnames.ora", "ORACLE_TNSNAMES_FILE_CONTENTS"),
    (
        "album_of_the_day_backend/website/tasks/systemd/task_runner/config.toml",
        "TASK_RUNNER_CONFIG_FILE_CONTENTS",
    ),
]


def expand_files() -> None:
    """Expands files from environment variables with Base64-encoded data of the file, if they are set."""
    for file_to_expand, environment_variable_to_use in FILES_TO_EXPAND:
        if os.path.exists(file_to_expand):
            logger.info(
                f"Not expanding {file_to_expand}: already exists on target filesystem."
            )
        else:
            if os.getenv(environment_variable_to_use, None) is not None:
                logger.info(
                    f"Expanding Base64 encoded environment variable {environment_variable_to_use}..."
                )
                os.makedirs(
                    os.path.dirname(file_to_expand), exist_ok=True
                )  # Create any directories of needed
                with open(file_to_expand, "wb") as new_file:
                    new_file.write(
                        base64.b64decode(os.environ[environment_variable_to_use])
                    )
                logger.info("File expanded.")
            else:
                raise FileNotFoundError(
                    f"Missing file {file_to_expand} in file system!"
                )


if __name__ == "__main__":
    expand_files()
