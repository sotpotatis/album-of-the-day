#prepare-environment-and-expand-files.sh
#Prepares an environment and expands files from it.
#Generate a script that will load the current environment into Bash
poetry run python debug_environment.py || exit 1
cd album_of_the_day_backend || exit 1
poetry run python ./../debug_environment.py #Debug the result
python ./album_of_the_day/expand_files_from_environment.py || exit 1 #Expand files
poetry run python ./../debug_environment.py #Debug the result
