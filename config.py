# import os
# import sys
# from pathlib import Path
# from typing import Union
#
#
# # --- Helper function for WSL path translation ---
# def wsl_path_to_windows(wsl_path: Union[str, Path]) -> Path:
#     """Translates a WSL path to a Windows path using the wslpath utility."""
#     try:
#         import subprocess
#         # Check if the wslpath utility is available
#         if 'WSL_DISTRO_NAME' in os.environ:
#             wsl_path_str = str(wsl_path)
#             result = subprocess.run(
#                 ['wslpath', '-w', wsl_path_str],
#                 capture_output=True,
#                 text=True,
#                 check=True
#             )
#             return Path(result.stdout.strip())
#     except (FileNotFoundError, subprocess.CalledProcessError):
#         pass
#     return Path(wsl_path)
#
#
# # --- Define the BASE_DIR with fallback logic ---
# def find_project_root(known_file: str) -> Path:
#     """
#     Searches for the project root by looking for a known file
#     (relative to this script).
#     """
#     # Get the absolute path of the current script's directory
#     script_dir = Path(__file__).resolve().parent
#
#     # Translate the path if running under WSL
#     if 'WSL_DISTRO_NAME' in os.environ:
#         script_dir = wsl_path_to_windows(script_dir)
#
#     # Walk up the directory tree to find the project root
#     for parent in script_dir.parents:
#         if (parent / known_file).exists():
#             return parent
#
#     # Fallback to the current directory if the known file isn't found
#     return script_dir
#
#
# # --- Central configuration for the project ---
# # Name a unique file that identifies the project root, e.g., 'README.md' or '.git'
# # For example, let's assume your project has a 'pyproject.toml' file at the root.
# PROJECT_MARKER_FILE = 'project.toml'
#
# BASE_DIR = find_project_root(PROJECT_MARKER_FILE)
#
# # --- Optional: Define a manual fallback if needed ---
# # If your project structure is unusual or the marker file is missing,
# # you can use a manual fallback.
# # Example: BASE_DIR_MANUAL_OVERRIDE = '/path/to/your/project'
# # if not BASE_DIR.exists():
# #     BASE_DIR = Path(BASE_DIR_MANUAL_OVERRIDE)
#
# # Print the determined BASE_DIR for debugging
# print(f"Project base directory is set to: {BASE_DIR}")

# Version 2

# import os
# import subprocess
# from pathlib import Path
# from typing import Union
#
#
# # --- Helper function for WSL path translation ---
# def wsl_path_to_windows(wsl_path: Union[str, Path]) -> Path:
#     """
#     Translates a WSL path (Linux format) to a Windows path (UNC format)
#     using the wslpath utility. This function is designed to be called
#     when the Python interpreter is running inside WSL, but you need
#     the Windows path representation (e.g., \\\\wsl$\\Ubuntu\\...).
#     """
#     try:
#         # Check if the script is running inside WSL by looking for a specific
#         # environment variable that WSL sets. This is more robust than checking os.name.
#         if 'WSL_DISTRO_NAME' in os.environ:
#             wsl_path_str = str(wsl_path)
#             # Execute the wslpath command to convert the path.
#             # '-w' flag means "Windows format path".
#             result = subprocess.run(
#                 ['wslpath', '-w', wsl_path_str],
#                 capture_output=True,
#                 text=True,
#                 check=True  # Raise an exception for non-zero exit codes
#             )
#             # wslpath adds a trailing newline, so strip it.
#             # Convert the result back into a pathlib.Path object.
#             return Path(result.stdout.strip())
#     except (FileNotFoundError, subprocess.CalledProcessError) as e:
#         # Handle cases where wslpath might not be found (e.g., not actually in WSL)
#         # or if the command fails for some reason.
#         # Print a warning but don't stop execution.
#         print(f"Warning: Could not translate path with wslpath. Error: {e}. Returning original path.")
#         pass  # Fall through to return the original path
#
#     # If not in WSL, or translation failed, return the original path as a Path object.
#     return Path(wsl_path)
#
#
# # --- Define the BASE_DIR with fallback logic ---
# def find_project_root(known_file: str) -> Path:
#     """
#     Searches for the project root by walking up the directory tree
#     from the current script's location, looking for a specified marker file.
#
#     Args:
#         known_file (str): The name of a file expected to be in the project's root directory.
#                           (e.g., 'pyproject.toml', 'README.md', '.git')
#
#     Returns:
#         pathlib.Path: The absolute path to the project's root directory.
#                       This path will be in Windows UNC format (\\\\wsl$\\...) if
#                       running via PyCharm's WSL interpreter, or native OS format otherwise.
#     """
#     # Get the absolute path of the current script file and its parent directory.
#     # .resolve() canonicalizes the path, handling symlinks etc.
#     script_path = Path(__file__).resolve()
#
#     # Determine the starting directory for the search.
#     # If running in WSL, translate it to the Windows path representation.
#     # Otherwise, it's already in the correct format for the OS.
#     current_search_path = wsl_path_to_windows(script_path.parent)
#
#     # Walk up the directory tree until the known_file is found.
#     # The list() conversion is needed because .parents returns an iterator.
#     # [current_search_path] is added to check the current directory first.
#     for parent in [current_search_path] + list(current_search_path.parents):
#         if (parent / known_file).is_file():
#             return parent
#
#     # If the known_file is not found, fall back to the initial script's directory (or its Windows equivalent).
#     print(
#         f"Warning: Project marker file '{known_file}' not found. Falling back to script's directory: {current_search_path}")
#     return current_search_path
#
#
# # --- Central configuration for the project ---
# # IMPORTANT: Replace 'pyproject.toml' with a file name that *uniquely* identifies
# # the root of *your* specific project (e.g., 'requirements.txt', 'setup.py', '.git').
# # This file MUST exist in your project's root directory.
# PROJECT_MARKER_FILE = 'project.toml'
#
# # Determine the base directory for the project using the robust logic above.
# BASE_DIR = find_project_root(PROJECT_MARKER_FILE)
#
# # --- Verification/Debugging output ---
# print(f"Project base directory is set to: {BASE_DIR}")
# # Inform about the path format being used
# if 'WSL_DISTRO_NAME' in os.environ:
#     print("Detected WSL environment. Using Windows UNC path format (\\\\wsl$\\...).")
# else:
#     print(f"Not detected WSL environment. Using native OS path format ({'Windows' if os.name == 'nt' else 'Posix'}).")
#
# --- Example Usage (demonstrates how to use BASE_DIR in other files) ---
# You can include this section or similar examples in your config.py
# or in a separate 'main.py' to show how to import and use BASE_DIR.

# def get_data_file_path(filename: str) -> Path:
#     """Returns a Path object for a file in the project's 'data' directory."""
#     return BASE_DIR / "data" / filename

# if __name__ == "__main__":
#     # This block runs only when config.py is executed directly.
#     # In other files, you would just 'from config import BASE_DIR'.
#     print("\n--- Example Paths ---")
#     example_input = get_data_file_path("input.csv")
#     example_output = BASE_DIR / "output" / "results.txt"

#     print(f"Example input file path: {example_input}")
#     print(f"Example output file path: {example_output}")

#     # The Path objects automatically handle the correct slash direction for the OS.
#     # You can pass them directly to functions like open().
#     # try:
#     #     with open(example_input, 'r') as f:
#     #         print(f"Successfully opened (or would open) {example_input}")
#     # except FileNotFoundError:
#     #     print(f"Could not find file: {example_input}")

import os
from pathlib import Path
from typing import Union

# --- Helper function for WSL path translation ---
# The original function is problematic because it always returns a Windows UNC path.
# We'll adjust the logic to only perform this translation when it's genuinely needed.
# However, for Python scripts running *inside* WSL, this function is unnecessary
# and causes the FileNotFoundError. We will remove it from the main path-finding logic.

# --- Define the BASE_DIR with fallback logic ---
def find_project_root(known_file: str) -> Path:
    """
    Searches for the project root by walking up the directory tree
    from the current script's location, looking for a specified marker file.

    Args:
        known_file (str): The name of a file expected to be in the project's root directory.

    Returns:
        pathlib.Path: The absolute path to the project's root directory,
                      in the correct format for the current operating system (WSL or Windows).
    """
    # Get the absolute path of the current script file and its parent directory.
    # .resolve() canonicalizes the path, handling symlinks etc.
    script_path = Path(__file__).resolve()

    # Determine the starting directory for the search.
    current_search_path = script_path.parent

    # Walk up the directory tree until the known_file is found.
    # The list() conversion is needed because .parents returns an iterator.
    # [current_search_path] is added to check the current directory first.
    for parent in [current_search_path] + list(current_search_path.parents):
        if (parent / known_file).is_file():
            return parent

    # If the known_file is not found, fall back to the initial script's directory.
    print(
        f"Warning: Project marker file '{known_file}' not found. Falling back to script's directory: {current_search_path}"
    )
    return current_search_path


# --- Central configuration for the project ---
# IMPORTANT: Replace 'project.toml' with a file name that *uniquely* identifies
# the root of *your* specific project (e.g., 'requirements.txt', 'setup.py', '.git').
# This file MUST exist in your project's root directory.
PROJECT_MARKER_FILE = 'project.toml'

# Determine the base directory for the project using the robust logic above.
BASE_DIR = find_project_root(PROJECT_MARKER_FILE)

# --- Verification/Debugging output ---
print(f"Project base directory is set to: {BASE_DIR}")
if 'WSL_DISTRO_NAME' in os.environ:
    print("Detected WSL environment. Using Linux path format (/mnt/d/...).")
else:
    print(f"Not detected WSL environment. Using native OS path format ({'Windows' if os.name == 'nt' else 'Posix'}).")

# --- Example Usage (demonstrates how to use BASE_DIR in other files) ---
# ... (same example as before) ...
