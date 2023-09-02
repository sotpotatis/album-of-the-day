#prepare-environment-and-expand-files.sh
#Prepares an environment and expands files from it.
#Generate a script that will load the current environment into Bash
poetry run python debug_environment.py
poetry run python load_dotenv_to_bash.py "./backend.env" "./load_env.sh" || exit 1
chmod +x "./load_env.sh" && ./load_env.sh #Load the environment
poetry run python debug_environment.py
# Test for empty variables (files environment variables are not supposed to be empty)
poetry run python debug_environment.py #Debug the result