#prepare-environment-and-expand-files.sh
#Prepares an environment and expands files from it.
#Generate a script that will load the current environment into Bash
poetry run python debug_environment.py || exit 1
poetry run python load_dotenv_to_bash.py "./backend.env" "./load_env.sh"
chmod +x "./load_env.sh" #Load the environment
poetry run python debug_environment.py #Debug the result
cd album_of_the_day_backend || exit 1
poetry run  ./load_env.sh && python ./album_of_the_day/expand_files_from_environment.py || exit 1 #Expand files
cd .. || exit 1
poetry run python debug_environment.py #Debug the result