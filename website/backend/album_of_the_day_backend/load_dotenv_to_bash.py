"""load_dotenv.py
Script to create a Bash script to load a dotenv file."""
from argparse import ArgumentParser, BooleanOptionalAction
from pathlib import Path
import dotenv, logging, os

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
cli = ArgumentParser()
cli.add_argument("source_file", type=Path, help="The dotenv file to load.")
cli.add_argument("target_file", type=Path, help="The target file to create.")
cli.add_argument(
    "--print_variables",
    help="Will not print the variables that were loaded.",
    default=True,
    action=BooleanOptionalAction,
)
# Parse arguments
arguments = cli.parse_args()
dotenv.find_dotenv(
    filename=arguments.source_file, raise_error_if_not_found=True
)  # Look for file
with open(arguments.target_file, "w") as target_file_object:
    # Parse variables
    loaded_values = dotenv.dotenv_values(dotenv_path=arguments.source_file)
    for loaded_value_name, loaded_value in loaded_values.items():
        if arguments.print_variables:
            logger.info(
                f"Loaded {loaded_value_name} (length {len(loaded_value)}) from environment file."
            )
            target_file_object.write(f'export {loaded_value_name}="{loaded_value}"\n')
logger.info(
    f"""Environment variable file created at {arguments.target_file}. Run it with eg.
chmod +x {arguments.target_file} && bash {arguments.target_file}"""
)
