"""expand-environment-files.sh
When using the Dockerfile with for example a CI/CD-tool,
you can store the content of secret files (wallet files for Oracle Cloud)
and configuration files inside environment variables.
This script expands the content of those variables - which should be the
file contents Base64-encoded (using the base64 Linux CLI as a baseline).
Note that environment variables will not be expanded to files if the target file
already exists."""
import base64
import os, logging
# Set up logging
logger = logging.getLogger(__name__)
FILES = [ # Format: (<file name>, <environment variable name>)
    ("album_of_the_day_backend/.wallet/cwallet.sso", "ORACLE_WALLET_FILE_CONTENTS"),
    ("album_of_the_day_backend/.wallet/sqlnet.ora", "ORACLE_SQLNET_FILE_CONTENTS"),
    ("album_of_the_day_backend/.wallet/tnsnames.ora", "ORACLE_TNSNAMES_FILE_CONTENTS"),
]
for file_to_expand, environment_variable_to_use in FILES:
    if os.path.exists(file_to_expand):
        logger.info(f"Not expanding {file_to_expand}: already expanded")
    else:
        logger.info(f"Expanding Base64 encoded environment variable {environment_variable_to_use}...")
        with open(file_to_expand, "wb") as new_file:
            new_file.write(base64.b64decode(os.environ[environment_variable_to_use]))
        logger.info("File expanded.")