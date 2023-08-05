"""prettier_format.py
Pre-commit script that formats the pieces of the application that should use Prettier"""
import os
os.chdir("website/frontend")
os.system("npx prettier **/* --write")