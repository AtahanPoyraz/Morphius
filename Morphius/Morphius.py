import os
import time

from config.settings import (
    AUTHOR,
    AUTHOR_EMAIL,
    BANNER,
    Color,
    LogLevel,
    PYTHON_VERSION,
    REPOSITORY_URL,
    TOOL_VERSION,
)

from manager.payload_manager import PayloadManager
from utils.console_utils import clear, exit, interrupt_handler, log_message
from utils.dependency_utils import check_requirements

class Morphius(PayloadManager):
    def __init__(self) -> None:
        super().__init__()

    @interrupt_handler
    def check_dependencies(self) -> None:
        """
        Checks if the required dependencies and libraries are installed. It also checks if 
        the Python version is at least 3.12.

        If any dependencies are missing, it prompts the user to install them. If Python version
        is incompatible, it exits the program.
        """
        try:
            clear()
            print(f"""{Color.BRIGHT_CYAN}{BANNER}{Color.RESET}
                \rVersion   : {TOOL_VERSION}
                \rAuthor    : {AUTHOR}
                \rContact   : {AUTHOR_EMAIL}
                \rRepository: {REPOSITORY_URL}
            """)
            missing_libraries: list[str] = check_requirements()

            if float(".".join(PYTHON_VERSION.split('.')[:-1])) <= 3.12:
                exit(
                    log_level=LogLevel.WARNING, 
                    text=f"Your Python version ({PYTHON_VERSION}) is below 3.12. Please upgrade to Python 3.12 or higher for compatibility."
                )

            if missing_libraries:
                exit(
                    log_level=LogLevel.WARNING,
                    text=(
                        f"Missing libraries detected: {', '.join(missing_libraries)}\n"
                        f"    Run: pip install {' '.join(missing_libraries)}\n"
                        f"    Or: make install (if supported)"
                    )
                )

            else:
                clear()
                log_message(
                    log_level=LogLevel.SUCCESS, 
                    text="All requirements are satisfied."
                )
                time.sleep(1.25)
                return

        except Exception as e:
            exit(
                log_level=LogLevel.ERROR, 
                text=f"An error occurred while checking requirements ({str(e)})"
            )

    @interrupt_handler
    def main(self):
        """
        The main method for running the application program.

        It displays the payloads, allows the user to select one, and prepares the selected payload.
        The method continues to run until the user selects "exit" or a valid payload.
        """
        try:
            if not os.path.exists(self.payloads_directory):
                exit(
                    log_level=LogLevel.ERROR, 
                    text=f"Payload directory does not exist: {self.payloads_directory}"
                )

            self.execute()

        except Exception as e:
            exit(
                log_level=LogLevel.ERROR, 
                text=f"An error occurred while starting program ({str(e)})"
            )

    @staticmethod
    def Run() -> None:
        """
        Static method that runs the entire application. It checks dependencies first,
        and then runs the main program.

        This is the entry point for running the application.
        """
        application = Morphius()
        application.check_dependencies()
        application.main()

if __name__ == "__main__":
    Morphius.Run()
