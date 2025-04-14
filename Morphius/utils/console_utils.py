import sys

from config.settings import *

def clear() -> None:
    """
    Clears the console screen based on the operating system.

    Description:
        This function uses `subprocess.call` to clear the terminal screen. 
        It automatically determines the command to use based on the operating system:
        - For Windows, it executes the "cls" command.
        - For Linux or other Unix-like systems, it executes the "clear" command.

    Usage:
        Call this function to refresh or clean up the console output.

    Note:
        The system's operating system is detected using the `System.OS` enum.
    """
    os.system("cls" if str(OS_NAME).lower() == "windows" else "clear")

def log_message(log_level: LogLevel, text: str) -> None:
    """
    Logs a message to the console with a specific log level and color.

    Args:
        log_level (LogLevel): The severity or type of the log message. 
                              Available levels are SUCCESS, WARNING, ERROR, DEBUG, INFO, and NOTICE.
        text (str): The message text to be displayed.

    Raises:
        ValueError: If the provided `log_level` is unsupported.

    Log Level Formatting:
        - SUCCESS: Bright green color.
        - WARNING: Bright yellow color.
        - ERROR: Bright red color.
        - DEBUG: Bright cyan color.
        - INFO: Bright magenta color.
        - NOTICE: Bright blue color.
    """
    match log_level:
        case LogLevel.SUCCESS:
            print(f"{Color.BRIGHT_GREEN}{log_level.value}{Color.RESET} {text}")

        case LogLevel.WARNING:
            print(f"{Color.BRIGHT_YELLOW}{log_level.value}{Color.RESET} {text}")

        case LogLevel.ERROR:
            print(f"{Color.BRIGHT_RED}{log_level.value}{Color.RESET} {text}")

        case LogLevel.DEBUG:
            print(f"{Color.BRIGHT_CYAN}{log_level.value}{Color.RESET} {text}")

        case LogLevel.INFO:
            print(f"{Color.BRIGHT_MAGENTA}{log_level.value}{Color.RESET} {text}")

        case LogLevel.NOTICE:
            print(f"{Color.BRIGHT_BLUE}{log_level.value}{Color.RESET} {text}")

        case _:
            raise ValueError(f"Unsupported log level: {log_level}")

def interrupt_handler(func: callable) -> callable:
    """
    A decorator to handle `KeyboardInterrupt` exceptions gracefully.

    This decorator wraps a function and ensures that when the user presses
    `Ctrl+C` during its execution, the program will handle the interruption
    cleanly by clearing the screen and displaying a logout message.

    Args:
        func (callable): The function to be wrapped by the decorator.

    Returns:
        callable: The wrapped function with added interrupt handling.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)    
        
        except KeyboardInterrupt:
            clear()
            print(f"Signed out of {TOOL_NAME}")

    return wrapper

def exit(log_level: LogLevel, text: str) -> None:
    """
    Clears the console and logs the given message with the specified log level, then exits the program.

    Args:
        log_level (LogLevel): The log level to be used for the log message. Determines the type of message (e.g., ERROR, WARNING, SUCCESS).
        text (str): The message to be logged. Provides information about the status or error.

    Exits the program with a status code:
        - 0 for non-error log levels 
        - 1 for ERROR log level.
    
    This function is a central exit handler that ensures consistent logging and graceful program termination.
    """
    clear()
    log_message(
        log_level=log_level, 
        text=text
    )
    
    sys.exit(1 if log_level == LogLevel.ERROR else 0)
