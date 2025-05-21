import os
import shutil
import subprocess
import sys
import time
from itertools import cycle
from typing import Iterable

from config.settings import ROOT_DIR, LogLevel

from utils.console_utils import exit, log_message

def get_requirements() -> list[str] | list:
    """
    Reads the requirements.txt file and returns a list of required libraries/tools.

    Returns:
        list[str]: A list of library or tool names defined in requirements.txt.
    """
    try:
        with open(os.path.join(ROOT_DIR, "requirements.txt"), "r+", encoding="UTF-8") as file:
            return [str(line).strip() for line in file.readlines()]

    except FileNotFoundError:
        log_message(
            log_level=LogLevel.ERROR, 
            text="requirements.txt file not found."
        )
        return []

def check_import(library: str) -> bool:
    """
    Checks if a Python library is installed and importable.

    Args:
        library (str): The name of the library to check.

    Returns:
        bool: True if the library can be imported, False otherwise.
    """
    try:
        __import__(library)
        return True

    except ModuleNotFoundError:
        return False

def check_command(command: str) -> bool:
    """
    Checks if a command is available on the system by running a simple check.

    Args:
        command (str): The command to check.

    Returns:
        bool: True if the command exists, False otherwise.
    """
    try:
        subprocess.run([command, '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) 
        return True

    except subprocess.CalledProcessError:
        return False

    except FileNotFoundError:
        return False

def check_cli_tool(library: str) -> bool:
    """
    Checks if a CLI tool is available on the system.

    Args:
        tool (str): The name of the CLI tool to check.

    Returns:
        bool: True if the tool is available, False otherwise.
    """
    return shutil.which(library) is not None

def loader() -> None:
    """
    Displays a loading animation in the console to indicate progress.

    This function cycles through a series of dots (".", "..", "...") three times
    and then exits automatically.
    """
    max_cycles: int = 1
    current_cycle: int = 0
    dots: Iterable[str] = cycle(["", ".", "..", "..."])

    while current_cycle < max_cycles:
        dot = next(dots)
        sys.stdout.write(f"\rChecking requirements{dot}")
        sys.stdout.flush()
        time.sleep(0.5)

        if dot == "...":
            current_cycle += 1  
    print()

def check_requirements() -> list[str]:
    """
    Checks the requirements defined in requirements.txt and identifies missing libraries or tools.

    This function performs the following checks for each required library or tool:
    1. Tries to import the library using `__import__`.
    2. Checks if the tool is available via the system's PATH using `shutil.which()`.
    3. Checks if the command is executable and available on the system using `subprocess.run()`.

    Additionally, `pyarmor` is specially handled by checking if the CLI tool or command is available, rather than performing an import check.

    The function adds any missing libraries or tools to a list and returns it.

    Returns:
        list[str]: A list of libraries or tools that are missing or unavailable on the system.
    """
    loader()
    missing_libraries: list[str] = []
    for requirement in get_requirements():
        library_name = "cv2" if requirement == "opencv-python" else requirement

        if library_name == "pyarmor":
            if not check_cli_tool(library_name) and not check_command(library_name):
                missing_libraries.append(library_name)
            continue  

        if not (check_import(library_name) or check_cli_tool(library_name) or check_command(library_name)):
            missing_libraries.append(library_name)

    return sorted(missing_libraries)

def install_requirements(missing_libraries: list[str]) -> None:
    """
    Installs the missing libraries/tools using pip.

    Args:
        missing_libraries (list[str]): A list of libraries/tools to install.

    Raises:
        subprocess.CalledProcessError: If the pip installation fails for any library.
    """
    for library in missing_libraries:
        try:
            subprocess.run(["pip", "install", library])
            log_message(
                log_level=LogLevel.SUCCESS,
                text=f"Installed {library}"
            )

        except subprocess.CalledProcessError as e:
            exit(
                log_level=LogLevel.ERROR,
                text=f"Failed to install {library}. Error: {str(e)}"
            )
