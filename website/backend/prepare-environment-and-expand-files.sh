#prepare-environment-and-expand-files.sh
#Prepares an environment and expands files from it.
#Generate a script that will load the current environment into Bash
poetry run python debug_environment.py
poetry run python load_dotenv_to_bash.py "./backend.env" "./load_env.sh"
chmod + ./load_env.sh && ./load_env.sh #Load the environment
# Test for empty variables (files environment variables are not supposed to be empty)
test -n "$ORACLE_WALLET_FILE_CONTENTS"
test -n "$ORACLE_SQLNET_FILE_CONTENTS"
test -n "$ORACLE_TNSNAMES_FILE_CONTENTS"
test -n "$TASK_RUNNER_CONFIG_FILE_CONTENTS"
poetry run python ./album_of_the_day_backend/album_of_the_day/expand_files_from_environment.py #Expand files
poetry run python debug_environment.py #Debug the result