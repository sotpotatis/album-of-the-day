"""debug_environment.py
Just a little debugger to debug environment variables."""
import os

for variable_name, variable_value in os.environ.items():
    if len(variable_name) >= 3:  # Add censorings to rest of variable value
        variable_value_minified = variable_value[0:2] + "*" * (len(variable_value) - 3)
    else:  # If variable is too short to be censored
        variable_value_minified = "***"
    print(f"{variable_name}:{variable_value_minified} (length {len(variable_value)})")
