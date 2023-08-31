"""load_dotenv.py
Script to load a dotenv file into memory."""
from argparse import ArgumentParser
from pathlib import Path
import dotenv, logging, os

logger = logging.getLogger(__name__)
cli = ArgumentParser()
cli.add_argument("source_file", type=Path, help="The dotenv file to load.")
cli.add_argument(
    "--no_print_variables",
    help="Will not print the variables that were loaded.",
    dest="print_variables",
    action="store_false",
)
cli.set_defaults(print_variables=True)
# Parse arguments
arguments = cli.parse_args()
dotenv.find_dotenv(
    filename=arguments.source_file, raise_error_if_not_found=True
)  # Look for file
dotenv.load_dotenv(dotenv_path=arguments.source_file)  # Load file
if arguments.print_variables:  # Change debug level if variables should be printed
    logging.basicConfig(level=logging.INFO)
    # ...and parse and print them!
    loaded_values = dotenv.dotenv_values(dotenv_path=arguments.source_file)
    for loaded_value_name, loaded_value in loaded_values.items():
        logger.info(
            f"Loaded {loaded_value_name} (length {len(loaded_value)}) from environment file."
        )
