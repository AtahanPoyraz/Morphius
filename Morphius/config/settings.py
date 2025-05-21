# -*- coding: utf-8 -*-

import getpass
import os
import platform
from enum import Enum

class Color(Enum):
    """
    Enumeration for ANSI color codes used to style text in terminal output.

    Attributes:
        - Each color is represented by an integer corresponding to its ANSI escape code.
        - The standard color codes range from 30 to 37 for regular colors.
        - The bright color codes range from 90 to 97 for enhanced or brighter colors.

    Regular Colors:
        - RED (\033[31m): Standard red color.
        - GREEN (\033[32m): Standard green color.
        - YELLOW (\033[33m): Standard yellow color.
        - BLUE (\033[34m): Standard blue color.
        - MAGENTA (\033[35m): Standard magenta (purple) color.
        - CYAN (\033[36m): Standard cyan (light blue) color.
        - WHITE (\033[37m): Standard white color.

    Bright Colors:
        - BRIGHT_RED (\033[91m): Bright red color.
        - BRIGHT_GREEN (\033[92m): Bright green color.
        - BRIGHT_YELLOW (\033[93m): Bright yellow color.
        - BRIGHT_BLUE (\033[94m): Bright blue color.
        - BRIGHT_MAGENTA (\033[95m): Bright magenta (purple) color.
        - BRIGHT_CYAN (\033[96m): Bright cyan (light blue) color.
        - BRIGHT_WHITE (\033[97m): Bright white color.

    Usage:
        - The colors can be used in conjunction with ANSI escape sequences to colorize terminal text.
        - Example of usage in terminal:
            `print(f"\033[{Color.RED.value}mThis is red text\033[0m")`

    Notes:
        - Use `\033[{color_code}m` to set the text color.
        - Always reset the color back to default with `\033[0m` after the text to prevent color leakage.

    Example:
        print(f"\033[{Color.BRIGHT_GREEN.value}mSuccess!\033[0m")
    """
    RED: str = "\033[31m"
    GREEN: str = "\033[32m"
    YELLOW: str = "\033[33m"
    BLUE: str = "\033[34m"
    MAGENTA: str = "\033[35m"
    CYAN: str = "\033[36m"
    WHITE: str = "\033[37m"
    RESET: str = "\033[0m"

    BRIGHT_RED: str = "\033[91m"
    BRIGHT_GREEN: str = "\033[92m"
    BRIGHT_YELLOW: str = "\033[93m"
    BRIGHT_BLUE: str = "\033[94m"
    BRIGHT_MAGENTA: str = "\033[95m"
    BRIGHT_CYAN: str = "\033[96m"
    BRIGHT_WHITE: str = "\033[97m"

    def __str__(self):
        return self.value

class LogLevel(Enum):
    """
    Enumeration for different log levels with associated symbols for text representation.

    Attributes:
        - Each log level is represented by a string with a unique symbol or code.

    Log Levels:
        - SUCCESS ("[+]"): Represents a successful operation or outcome.
        - DEBUG ("[*]"): Represents debug information for troubleshooting and development.
        - INFO ("[?]"): Represents informational messages or updates.
        - WARNING ("[!]"): Represents a warning about potential issues.
        - NOTICE ("[#]"): Represents general notices or updates.
        - ERROR ("[X]"): Represents an error or failure in the system.

    Usage:
        - Log levels help categorize log messages for different purposes (debugging, warnings, errors, etc.).
        - Example of usage in code:
            `log_message(LogLevel.SUCCESS, "Operation completed successfully.")`
            `log_message(LogLevel.ERROR, "An error occurred during the operation.")`

    Example:
        print(f"{LogLevel.SUCCESS.value} Success!")
        print(f"{LogLevel.ERROR.value} Error!")
    """
    SUCCESS: str = "[+]"
    DEBUG: str = "[*]"
    INFO: str = "[?]"
    WARNING: str = "[!]"
    NOTICE: str = "[#]"
    ERROR: str = "[X]"

    def __str__(self):
        return self.value

# The name of the tool being used.
TOOL_NAME: str = "Morphius"

# The version of tool.
TOOL_VERSION: str = "1.0.0"

# The author of tool.
AUTHOR: str = "AtahanPoyraz"

# The absolute path to the root directory where the tool is located. 
# It finds the directory by splitting the file path and retrieving the part up to the directory containing the tool.
ROOT_DIR: str = os.path.join(os.path.abspath("."))

# The username of the current user, retrieved using the `getpass` module.
USER_NAME: str = getpass.getuser()

# The operating system name (e.g., "Windows", "Linux", "Darwin") using the `platform` module.
OS_NAME: str = platform.system()  

# The version of the operating system.
OS_VERSION: str = platform.version()

# The release of the operating system.
OS_RELEASE: str = platform.release()

# The architecture of the machine (e.g., "x86_64", "AMD64") using the `platform` module.
MACHINE: str = platform.machine()  

# The version of Python currently being used.
PYTHON_VERSION: str = platform.python_version()

# The flag or prompt string that appears when the application is waiting for user input.
UPPER_FLAG: str = f"╭{Color.BRIGHT_CYAN}─{Color.CYAN}─{Color.BRIGHT_BLUE}{{{Color.BRIGHT_CYAN}{TOOL_NAME}{Color.BRIGHT_BLUE}}}{Color.RESET}"

DOWN_FLAG: str = f"╰{Color.BRIGHT_CYAN}─{Color.CYAN}─{Color.BRIGHT_BLUE}>{Color.RESET} "
