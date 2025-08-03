import ast
import importlib
import os
import re
import subprocess
import textwrap
import time

from config.settings import DOWN_FLAG, ROOT_DIR, TOOL_NAME, UPPER_FLAG
from utils.console_utils import Color, LogLevel, clear, exit, log_message, task_handler

class PayloadManager():
    """
    This class is responsible for managing payload files in a specified directory.
    It includes functionality for loading, checking, and generating payloads,
    as well as obfuscating and building standalone executables.
    """
    def __init__(self) -> None:
        self.__payloads: dict[str, list[str]] = {}
        self.__payload_cache: dict[str, any] = {} 
        self.__payloads_directory: str = os.path.join(ROOT_DIR, "payloads")

    @property
    def payloads(self) -> dict[str, list[str]]:
        """
        Returns the list of payloads that are available.

        This property returns the list of payload files loaded into memory.
        """
        return self.__payloads

    @payloads.setter
    def payloads(self, value: dict[str, list[str]]) -> None:
        """
        Setter for the payloads property.

        Args:
            value (list): A list of payloads to be set.

        Raises:
            ValueError: If the value is not a list.
        """
        if isinstance(value, dict) and all(isinstance(v, list) for v in value.values()):
            self.__payloads = value

        else:
            raise ValueError("Payloads must be a list.")

    @property
    def payload_cache(self) -> dict[str, any]:
        """
        Returns the payload cache.

        This property returns the cache containing descriptions of the payloads to avoid
        repeated file reading for the same payload.
        """
        return self.__payload_cache

    @payload_cache.setter
    def payload_cache(self, value: dict[str, any]) -> None:
        """
        Setter for the payload cache property.

        Args:
            value (dict): The new cache to be set for payload descriptions.

        Raises:
            ValueError: If the value is not a dictionary.
        """
        if isinstance(value, dict):
            self.__payload_cache = value

        else:
            raise ValueError("Payload cache must be a dictionary.")

    @property
    def payloads_directory(self) -> str:
        """
        Returns the path to the payloads directory.

        This property returns the path to the directory where payloads are stored.
        """
        return self.__payloads_directory

    @payloads_directory.setter
    def payloads_directory(self, value: str) -> None:
        """
        Setter for the payloads directory property.

        Args:
            value (str): The new path to the payloads directory.

        Raises:
            ValueError: If the value is not a string.
        """
        if isinstance(value, str):
            self.__payloads_directory = value

        else:
            raise ValueError("Payloads directory path must be a string.")

    def _get__payloads(self, size: int) -> dict[int, list[str]]:
        """
        Retrieves payload files from the payload directory and splits them into pages of a specified size.

        Args:
            size (int): Number of payloads per page.

        Returns:
            dict[int, list[str]]: A dictionary where keys are page numbers (starting from 1) and values are lists of payload file paths.
        """
        try:
            payloads: list[str] = []
            for root, _, files in os.walk(self.__payloads_directory):
                for file in files:
                    if os.path.isfile(os.path.join(root, file)):
                        payloads.append(os.path.relpath(os.path.join(root, file), self.__payloads_directory))

            return {index: payloads[page: page + size] for index, page in enumerate(range(0, len(payloads), size), start=1)}

        except FileNotFoundError:
            exit(
                log_level=LogLevel.ERROR, 
                text=f"Payload directory not found: {self.__payloads_directory}"
            )

        except PermissionError:
            exit(
                log_level=LogLevel.ERROR, 
                text=f"Permission denied to access: {self.__payloads_directory}"
            )

    def _check_payload(self, payload: str) -> bool:
        """
        Checks if the specified payload file exists in the payloads directory.

        Args:
            payload (str): The name of the payload file to check.

        Returns:
            bool: True if the payload exists, otherwise False.
        """
        return os.path.exists(os.path.join(self.__payloads_directory, payload))

    def _extract_descriptions(self, payload: str) -> list[str]:
        """
        Extracts the descriptions from a given payload file.

        Args:
            payload (str): The name of the payload file.

        Returns:
            list[str]: A list of description strings found within the payload file.
        """
        if payload in self.__payload_cache:
            return self.__payload_cache[payload]

        descriptions: list[str] = []
        payload_path: str = os.path.join(self.__payloads_directory, payload)

        if not os.path.isfile(payload_path):
            exit(
                log_level=LogLevel.ERROR, 
                text=f"Payload file does not exist: {payload_path}"
            )

        try:
            with open(payload_path, "r", encoding="UTF-8") as file:
                descriptions = [
                    line.removeprefix("#//").strip()
                    for line in file
                    if line.startswith("#//")
                ]

            if not descriptions:
                descriptions.append("No description available.")

            self.__payload_cache[payload] = descriptions

        except PermissionError:
            exit(
                log_level=LogLevel.ERROR, 
                text=f"Permission denied to read file: {payload_path}"
            )

        except Exception as e:
            exit(
                log_level=LogLevel.ERROR, 
                text=f"An unexpected error occurred while reading {payload_path}: {str(e)}"
            )

        return descriptions

    def _extract_imports(self, payload_path: str) -> dict[str, list[str]]:
        """
        This function extracts all import statements (both standard and from module) from a Python file,
        categorizes them into modules and imported items, and returns them in a sorted manner.

        Args:
            payload_path (str): The path to the Python file from which imports are to be extracted.

        Returns:
            dict[str, list[str]]: A dictionary with two keys:
                - "modules": A list of unique module names sorted alphabetically.
                - "imported_items": A list of unique imported item names (including aliases) sorted alphabetically.
        """
        imported_items: set[str] = set()
        imported_modules: set[str] = set()

        with open(payload_path, "r", encoding="UTF-8") as file:                        
            for node in ast.parse(file.read()).body:
                if isinstance(node, ast.Import): 
                    for alias in node.names:
                        imported_items.add(alias.name)
                        imported_items.add(alias.asname)

                elif isinstance(node, ast.ImportFrom):  
                    imported_modules.add(node.module)
                    for alias in node.names:
                        imported_items.add(alias.name)
                        imported_items.add(alias.asname)

            imported_items.discard(None)
            imported_modules.discard(None)

        return {"modules": list(sorted(imported_modules)), "items": list(sorted(imported_items))}

    def _extract_placeholders(self, payload: str) -> list[str]:
        """
        Extracts and returns all unique placeholders from the payload file.

        Placeholders are defined in the `${VARIABLE_NAME}` format within the payload.

        Args:
            payload (str): The name of the payload file to read and extract placeholders from.

        Returns:
            list[str]: A list of unique placeholders found within the payload file.
        """
        placeholders: list[str] = []

        with open(os.path.join(self.__payloads_directory, payload), "r+", encoding="UTF-8") as file:
            for line in file.readlines():
                placeholders.extend(re.findall(r"\$\{([A-Z_]+)\}", line))

        return list(sorted(set(placeholders)))

    def _load_variables(self, variables: list[str]):
        """
        Loads specified variable names as class attributes.

        This method checks whether the specified variables are already class attributes,
        and if not, sets them to 'NOT SET'.

        Args:
            variables (list[str]): A list of variable names to be loaded as class attributes.
        """
        for variable in variables:
            if not hasattr(self, variable.lower()):
                setattr(self, variable.lower(), getattr(self, variable.lower(), "NOT SET"))

    def _validate_input(self, prompt: str, condition: callable, failure_message: str) -> str:
        """
        Prompts the user for input and validates it against the provided condition. 
        Keeps asking for input until the condition is met, then returns the valid input.

        Args:
            prompt (str): The message displayed to the user, asking for the required input.
            condition (callable): A function that checks whether the input is valid. 
            failure_message (str): The message displayed when the input is invalid.

        Returns:
            str: The valid input provided by the user.
        """
        while True:
            value: str = input(prompt)
            if condition(value):
                return value

            else:
                log_message(
                    log_level=LogLevel.WARNING, 
                    text=failure_message
                )

    def _write_payload(self, payload_name: str, payload_source: str, payload_variables: dict[str, any]) -> None:
        """
        Reads the specified payload source file, performs modifications (such as replacing function and class names with random strings),
        and writes the modified content to the output file.

        Args:
            - 'payload_name' (str): The name of the output file to be created.
            - 'payload_source' (str): The path of the source file to be read and processed.
            - 'payload_variables' (dict): A dictionary where keys represent variables to be replaced in the payload, and values are the replacement values.

        Raises:
            FileNotFoundError: If the source file specified by 'payload_source' does not exist.
            OSError, PermissionError: If there is an issue with file writing (e.g., permission issues or file system errors).
            Exception: If any other unexpected error occurs during the process.
        """
        try:            
            output_path: str = os.path.join(ROOT_DIR, "dist", "generate", f"{payload_name}.py")

            if not os.path.exists(output_path):
                os.makedirs(os.path.dirname(output_path), exist_ok=True)

            with open(payload_source, "r", encoding="UTF-8") as p:
                content: str = p.read()

            for name, value in payload_variables.items():
                content: str = content.replace(f"${{{name}}}", value)

            with open(output_path, "w", encoding="UTF-8") as p:
                p.write(content)

        except FileNotFoundError:
            exit(
                log_level=LogLevel.ERROR, 
                text=f"Payload file '{os.path.basename(payload_source)}' not found in '{os.path.dirname(payload_source) or '.'}'"
            )

        except (OSError, PermissionError) as e:
            exit(
                log_level=LogLevel.ERROR, 
                text=f"Failed to write payload due to a file error ({payload_source}): {str(e)}"
            )

        except Exception as e:
            exit(
                log_level=LogLevel.ERROR, 
                text=f"An unexpected error occurred while writing payload ({payload_source}): {str(e)}"
            )

    def _obfuscate_payload(self, payload_name: str) -> None:
        """
        Obfuscates a Python payload using the PyArmor tool.

        This method calls the PyArmor command-line tool to obfuscate the specified payload
        and saves the obfuscated file in the dist/obfuscate directory.

        Args:
            - payload_name (str): The name of the payload to obfuscate.
        """
        try:
            result: int = subprocess.call([
                "pyarmor", 
                "generate", 
                "--output", 
                os.path.join(ROOT_DIR, "dist", "obfuscate", payload_name), 
                os.path.join(ROOT_DIR, "dist", "generate", f"{payload_name}.py")
            ])

            if result != 0:
                log_message(
                    log_level=LogLevel.ERROR, 
                    text="Payload build failed! Please check the logs for more details."
                )
                return

            log_message(
                log_level=LogLevel.SUCCESS, 
                text="Payload obfuscation completed successfully!"
            )

        except Exception as e:
            exit(
                log_level=LogLevel.ERROR, 
                text=f"An unexpected error occurred while obfuscating payload ({payload_name}): {str(e)}"
            )

    def _build_payload(self, payload_name: str, payload_source: str, payload_icon: str, payload_path: str) -> None:
        """
        Builds a standalone executable from a Python payload using PyInstaller.

        This method calls PyInstaller to generate a standalone executable from the obfuscated
        Python payload and stores the executable in the specified directory.

        Args:
            - payload_name (str): The name of the payload being built.
            - payload_source (str): Path to the source template file.
            - payload_icon (str): The path of the payload icon.
            - payload_path (str, optional): The directory to store the executable (default is 'dist').
        """
        try:
            result: int = subprocess.call([
                "pyinstaller",
                "--clean",
                "--onefile",
                "--noconsole",
                "--workpath", os.path.join(ROOT_DIR, "dist", "build", payload_name),
                "--specpath", os.path.join(ROOT_DIR, "dist", "build", payload_name),
                "--distpath", os.path.join(ROOT_DIR, payload_path if payload_path else "dist"),
                "--add-data", f"{os.path.join(ROOT_DIR, 'dist', 'obfuscate', payload_name, 'pyarmor_runtime_000000')}{os.pathsep}pyarmor_runtime_000000",
                *(["--icon", payload_icon] if payload_icon and os.path.exists(payload_icon) else []),
                *([f"--hidden-import={lib}" for lib in self._extract_imports(payload_source)["modules"]]),
                os.path.join(ROOT_DIR, "dist", "obfuscate", payload_name, f"{payload_name}.py")
            ])

            if result != 0:
                log_message(
                    log_level=LogLevel.ERROR, 
                    text="Payload build failed! Please check the logs for more details."
                )
                return

            log_message(
                log_level=LogLevel.SUCCESS, 
                text=f"Payload build completed successfully! \nPayload saved to: {os.path.join(ROOT_DIR, payload_path if payload_path else 'dist')}"
            )

        except Exception as e:
            exit(
                log_level=LogLevel.ERROR, 
                text=f"An unexpected error occurred while building payload ({payload_name}): {str(e)}"
            )

    @task_handler
    def _generate_payload(self, payload_source: str, payload_name: str, payload_icon: str, payload_path: str, payload_variables: dict[str, any]) -> None:
        """
        Generates a Python program by replacing placeholders with specified values.

        After generating the program, it is obfuscated and compiled into a standalone executable.

        Args:
            payload_source (str): The template payload file to use.
            payload_name (str): The name of the generated executable.
            payload_icon (str, optional): The path to the icon file (default is empty, no icon).
            payload_path (str, optional): The directory to save the generated executable (default is "dist/build").
            payload_variables (dict[str, str]): A dictionary of placeholder values to be replaced in the payload.
        """
        clear()
        if not os.path.isfile(payload_source):
            exit(
                log_level=LogLevel.ERROR, 
                text=f"Payload file '{os.path.basename(payload_source)}' not found in '{payload_source}'."
            )

        self._write_payload(
            payload_name=payload_name,
            payload_source=payload_source,
            payload_variables=payload_variables,
        )

        self._obfuscate_payload(
            payload_name=payload_name,
        )

        self._build_payload(
            payload_name=payload_name,
            payload_source=payload_source,
            payload_icon=payload_icon,
            payload_path=payload_path,
        )

    def _help_menu(self) -> None:
        """
        Displays a formatted help menu showing available commands and their descriptions.

        This function constructs a table-like structure with two columns:
        - "COMMANDS": Lists the commands that can be used.
        - "DESCRIPTIONS": Provides a short explanation of what each command does.

        The output is styled with color and borders for better readability.
        After displaying the menu, it waits for user input to proceed.
        """

        # Dictionary of available commands and their descriptions for navigating and using payloads.
        AVAILABLE_COMMANDS: dict[str, str] = {
            '"use [payload_name]" / "use [payload_number]"': "Select a specific payload by name or number.",
            '"page [page_number]"'                         : "Navigate to a specific page of payloads.",
            '"exit"'                                       : "Exit the program.",
        }

        # Calculate the maximum width of the command names dynamically based on their lengths
        COMMAND_WIDTH: int = max(len(command) for command in AVAILABLE_COMMANDS)

        # Add 2 to the command width to account for padding and frame borders
        COMMAND_FRAME_WIDTH: int = (COMMAND_WIDTH + 6)

        # Calculate the maximum width of the descriptions based on their longest entry
        DESCRIPTION_WIDTH: int = max(len(description) for description in AVAILABLE_COMMANDS.values())

        # Add 2 to the description width to ensure proper padding and frame borders
        DESCRIPTION_FRAME_WIDTH: int = (DESCRIPTION_WIDTH + 2)

        clear()
        print(f"╔{'═' * COMMAND_FRAME_WIDTH}╦{'═' * DESCRIPTION_FRAME_WIDTH}╗")
        print(f"║{Color.BRIGHT_CYAN}{'COMMANDS':^{COMMAND_FRAME_WIDTH}}{Color.RESET}║{Color.BRIGHT_CYAN}{'DESCRIPTIONS':^{DESCRIPTION_FRAME_WIDTH}}{Color.RESET}║")
        print(f"╠{'═' * COMMAND_FRAME_WIDTH}╬{'═' * DESCRIPTION_FRAME_WIDTH}╣")

        for index, (command, description) in enumerate(AVAILABLE_COMMANDS.items(), start=1):
            print(f"║[{Color.BRIGHT_CYAN}{index:02d}{Color.RESET}] {command:<{COMMAND_WIDTH}} : {description:<{DESCRIPTION_WIDTH}} ║")

        print(f"╚{'═' * COMMAND_FRAME_WIDTH}╩{'═' * DESCRIPTION_FRAME_WIDTH}╝")
        input(f"{Color.BRIGHT_CYAN}{'>> Press ENTER to continue <<':^{COMMAND_FRAME_WIDTH + DESCRIPTION_FRAME_WIDTH}}{Color.RESET}\n")

    def _payloads_menu(self, page: int) -> None:
        """
        Displays the payloads menu in a formatted table, showing payload names and descriptions.

        Args:
            page (int): The page number to display.

        Returns:
            None: This function only prints the payload menu to the terminal.

        Raises:
            ValueError: If no payloads are found, an error message is logged and the program exits.

        Function Details:
            - Clears and reloads payloads from the directory (5 payloads per page).
            - Calculates dynamic widths for payload names and descriptions to maintain clean formatting.
            - Displays a formatted table with payload indexes, names, and descriptions.
            - Supports multi-line wrapped descriptions to fit the terminal width nicely.
            - Shows the current page number and usage hint for navigation.
        """
        try:
            self.__payloads.clear()
            self.__payloads = self._get__payloads(size=3)

            page__payloads: list[str] = self.__payloads.get(page, [])
            if not page__payloads:
                return self._payloads_menu(page=page - 1) if page > 1 else exit(log_level=LogLevel.ERROR, text="No payload found. Please ensure the payload exists and try again.")

            # Calculate the maximum width of the payload names dynamically based on their lengths
            PAYLOAD_WIDTH: int = max([len(os.path.splitext(item)[0]) for sublist in self.__payloads.values() for item in sublist])

            # Add 6 to the payload width to account for additional padding and frame borders
            PAYLOAD_FRAME_WIDTH: int = (PAYLOAD_WIDTH + 6)

            # Set a fixed width for the payload description column to ensure consistent alignment
            PAYLOAD_DESCRIPTION_WIDTH: int = 80

            # Add 2 to the description width to account for additional padding and frame borders
            PAYLOAD_DESCRIPTION_FRAME_WIDTH: int = (PAYLOAD_DESCRIPTION_WIDTH + 2)

            # Calculates the global payload index based on the current page number.
            GLOBAL_INDEX: int = ((page - 1) * len(self.__payloads.get(1, [])) + 1)

            def wrap_text(text: str, width: int) -> list[str]:
                """
                Wraps a given text to the specified width using textwrap.
                """
                return textwrap.wrap(text, width)

            clear()
            print(f"╔{'═' * PAYLOAD_FRAME_WIDTH}╦{'═' * (PAYLOAD_DESCRIPTION_FRAME_WIDTH)}╗")
            print(f"║{Color.BRIGHT_CYAN}{'PAYLOADS':^{PAYLOAD_FRAME_WIDTH}}{Color.RESET}║{Color.BRIGHT_CYAN}{'DESCRIPTIONS':^{PAYLOAD_DESCRIPTION_FRAME_WIDTH}}{Color.RESET}║")
            print(f"╠{'═' * PAYLOAD_FRAME_WIDTH}╬{'═' * (PAYLOAD_DESCRIPTION_FRAME_WIDTH)}╣")

            for index, payload in enumerate(page__payloads, start=GLOBAL_INDEX):
                wrapped_lines: list[str] = []
                for sentence in " ".join(self._extract_descriptions(payload=payload)).split(". "):
                    wrapped_lines.extend(wrap_text((f"{sentence}." if not sentence.endswith(".") else sentence).strip(), PAYLOAD_DESCRIPTION_WIDTH))

                print(f"║[{Color.BRIGHT_CYAN}{index:02d}{Color.RESET}] {os.path.splitext(payload)[0]:<{PAYLOAD_WIDTH}} : {wrapped_lines[0]:<{PAYLOAD_DESCRIPTION_WIDTH}} ║")

                for line in wrapped_lines[1:]:
                    print(f"║{' ' * PAYLOAD_FRAME_WIDTH}║ {f'{line.lstrip()}':<{PAYLOAD_DESCRIPTION_WIDTH}} ║")

                print(f"╠{'═' * PAYLOAD_FRAME_WIDTH}╬{'═' * (PAYLOAD_DESCRIPTION_FRAME_WIDTH)}╣")

            print(f"║{Color.BRIGHT_CYAN}{f'HELP':^{PAYLOAD_FRAME_WIDTH}}{Color.RESET}║{' Type `help` to show available commands.':<{PAYLOAD_DESCRIPTION_FRAME_WIDTH}}║")
            print(f"╠{'═' * PAYLOAD_FRAME_WIDTH}╩{'═' * (PAYLOAD_DESCRIPTION_FRAME_WIDTH)}╣")
            print(f"║{Color.BRIGHT_CYAN}{f'PAGE {page} of {len(self.__payloads.keys())}':^{PAYLOAD_FRAME_WIDTH + PAYLOAD_DESCRIPTION_FRAME_WIDTH}}{Color.RESET} ║")
            print(f"╚{'═' * PAYLOAD_FRAME_WIDTH}═{'═' * (PAYLOAD_DESCRIPTION_FRAME_WIDTH)}╝")

        except ValueError:
            exit(
                log_level=LogLevel.ERROR, 
                text="No payload found. Please ensure the payload exists and try again."
            )

    def execute(self) -> None:
        """
        Handles the user interface for selecting a payload or navigating the payload menu.

        This function provides an interactive menu where the user can:
        - Select a payload by number or name using the "use [number/name]" command.
        - Navigate between pages using "page [number]".
        - Exit the menu with the "exit" command.

        Function Details:
            - Displays the payload menu starting from page 1.
            - Supports both numeric payload selection and selection by payload name.
            - Supports page navigation and exits cleanly when the user types "exit".
            - Handles invalid inputs gracefully, with warnings and retries.
            - Errors are logged with appropriate messages for better debugging.
        """
        page: int = 1
        while True:
            try:
                self._payloads_menu(page=page)

                print(UPPER_FLAG)
                option: str = input(DOWN_FLAG)
                match option:
                    case option if option.startswith("use") and (len(option.split(" ")) > 1):
                        all__payloads: list[str] = [item for sublist in self.__payloads.values() for item in sublist]

                        if option.split(" ")[1].isdigit() and int(option.split(" ")[1]) > 0:
                            if 0 <= int(option.split(" ")[1]) - 1 < len(all__payloads):
                                self._prepare_payload(
                                    payload=os.path.join(self.__payloads_directory, all__payloads[int(option.split(" ")[1]) - 1])
                                )
                                break

                            else:
                                log_message(
                                    LogLevel=LogLevel.WARNING, 
                                    text="Invalid payload number. Please try again."
                                )
                                time.sleep(1.25)
                                continue

                        elif " ".join(option.split(" ")[1:]).strip() in [os.path.splitext(payload)[0] for payload in all__payloads]:
                            self._prepare_payload(
                                payload=os.path.join(
                                    self.__payloads_directory, 
                                    next(
                                        (payload for payload in all__payloads if os.path.splitext(payload)[0] == " ".join(option.split(" ")[1:]).strip()), None
                                    )
                                )
                            )
                            break

                        else:
                            log_message(
                                log_level=LogLevel.WARNING, 
                                text="Invalid payload option. Please try again."
                            )
                            time.sleep(1.25)
                            continue  

                    case option if option.startswith("page") and (len(option.split(" ")) > 1):
                        if not ((int(option.split(" ")[1]) > len(self.__payloads)) or (int(option.split(" ")[1]) == 0)):
                            page = int(option.split(" ")[1])

                        else:
                            log_message(
                                log_level=LogLevel.WARNING,
                                text="Invalid page number. Please try again."
                            )
                            time.sleep(1.25)  
                            continue

                    case option if option.lower() == "help":
                        self._help_menu()
                        continue

                    case option if option.lower() == "exit":
                        exit(
                            log_level=LogLevel.NOTICE,
                            text=f"Signed out of {TOOL_NAME}."
                        )

                    case _:
                        log_message(
                            log_level=LogLevel.WARNING,
                            text="Invalid option. Please try again."
                        )
                        time.sleep(1.25)  
                        continue

            except IndexError:
                log_message(
                    log_level=LogLevel.WARNING,
                    text="Invalid payload number. Please try again."
                )
                time.sleep(1.25)  
                continue

            except Exception:
                exit(
                    log_level=LogLevel.ERROR, 
                    text="An error occurred while selecting option."
                )

    def _help_prepare(self) -> None:
        """
        Displays a formatted help menu showing available commands and their descriptions.

        This function constructs a table-like structure with two columns:
        - "COMMANDS": Lists the commands that can be used.
        - "DESCRIPTIONS": Provides a short explanation of what each command does.

        The output is styled with color and borders for better readability.
        After displaying the menu, it waits for user input to proceed.
        """
        [
            ' - Use "back" to go back.',
            ' - Use "exit" to exit program.',
            ' - Use "set [parameter] [value]" to update values.',
            ' - Use "generate" to create the payload with current settings.'
        ]

        # Dictionary of available commands and their descriptions for navigating and using payloads.
        AVAILABLE_COMMANDS: dict[str, str] = {
            "'back'"                    : "Go back to the previous menu.",
            "'exit'"                    : "Exit the program.",
            "'set [parameter] [value]'" : "Set a variable to a specific value.",
            "'generate'"                : "Generate the payload with current settings.",
        }

        # Calculate the maximum width of the command names dynamically based on their lengths
        COMMAND_WIDTH: int = max(len(command) for command in AVAILABLE_COMMANDS)

        # Add 2 to the command width to account for padding and frame borders
        COMMAND_FRAME_WIDTH: int = (COMMAND_WIDTH + 6)

        # Calculate the maximum width of the descriptions based on their longest entry
        DESCRIPTION_WIDTH: int = max(len(description) for description in AVAILABLE_COMMANDS.values())

        # Add 2 to the description width to ensure proper padding and frame borders
        DESCRIPTION_FRAME_WIDTH: int = (DESCRIPTION_WIDTH + 2)

        clear()
        print(f"╔{'═' * COMMAND_FRAME_WIDTH}╦{'═' * DESCRIPTION_FRAME_WIDTH}╗")
        print(f"║{Color.BRIGHT_CYAN}{'COMMANDS':^{COMMAND_FRAME_WIDTH}}{Color.RESET}║{Color.BRIGHT_CYAN}{'DESCRIPTIONS':^{DESCRIPTION_FRAME_WIDTH}}{Color.RESET}║")
        print(f"╠{'═' * COMMAND_FRAME_WIDTH}╬{'═' * DESCRIPTION_FRAME_WIDTH}╣")

        for index, (command, description) in enumerate(AVAILABLE_COMMANDS.items(), start=1):
            print(f"║[{Color.BRIGHT_CYAN}{index:02d}{Color.RESET}] {command:<{COMMAND_WIDTH}} : {description:<{DESCRIPTION_WIDTH}} ║")

        print(f"╚{'═' * COMMAND_FRAME_WIDTH}╩{'═' * DESCRIPTION_FRAME_WIDTH}╝")
        input(f"{Color.BRIGHT_CYAN}{'>> Press ENTER to continue <<':^{COMMAND_FRAME_WIDTH + DESCRIPTION_FRAME_WIDTH}}{Color.RESET}\n")


    def _preparation_menu(self, payload: str, variables: list[str]) -> None:
        """
        Displays the preparation menu with payload details and instructions.

        Args:
            payload (str): The selected payload's path to display.

        Inner Function:
            truncate_text(text: str, max_length: int) -> str:
                Shortens a given text to the specified length and appends "..." if truncated.

        Notes:
            - Shows the payload details and current variable values.
            - Provides hints and options for the user (e.g., 'set', 'back', 'generate').
        """
        def truncate_text(text: str, max_length: int) -> str:
            """Truncate text to a specific length and append '...' if necessary."""
            if len(text) <= max_length:
                return text

            return text[:max_length - 3] + "..." if max_length > 3 else text[:max_length]

        payload: str = os.path.relpath(payload, self.__payloads_directory).rpartition(".")[0]

        # VARIABLE_WIDTH: Maximum length of variable names in variables and "PAYLOAD".
        VARIABLE_WIDTH: int = max([len(variable) for variable in variables] + [len("PAYLOAD")])

        # VARIABLE_FRAME_WIDTH: Width for the frame around the variable name, with 2 units of padding.
        VARIABLE_FRAME_WIDTH: int = (VARIABLE_WIDTH + 2) 

        # VALUE_WIDTH: Determines the maximum width based on the truncated variable values, payload length, and a minimum width of 60 characters.
        VALUE_WIDTH: int = max(max(len(truncate_text(getattr(self, variable.lower()), (len(payload)))) for variable in variables), len(payload), 60)

        # VALUE_FRAME_WIDTH: Width for the frame around the variable values, with 2 units of padding.
        VALUE_FRAME_WIDTH: int = (VALUE_WIDTH + 2)    

        clear()
        print(f"╔{'═' * VARIABLE_FRAME_WIDTH}═{'═' * VALUE_FRAME_WIDTH}╗")
        print(f"║{Color.BRIGHT_CYAN}{TOOL_NAME:^{VARIABLE_FRAME_WIDTH + VALUE_FRAME_WIDTH}}{Color.RESET} ║")
        print(f"╠{'═' * VARIABLE_FRAME_WIDTH}╦{'═' * VALUE_FRAME_WIDTH}╣")

        for variable in variables:
            truncate_var: str = truncate_text(getattr(self, variable.lower()), len(payload) if len(payload) >= VALUE_WIDTH else VALUE_WIDTH)
            print(f"║ {Color.BRIGHT_CYAN}{variable:<{VARIABLE_WIDTH}}{Color.RESET} : {truncate_var:<{VALUE_WIDTH}} ║")

        print(f"╠{'═' * VARIABLE_FRAME_WIDTH}╬{'═' * VALUE_FRAME_WIDTH}╣")
        print(f"║ {Color.BRIGHT_CYAN}{'PAYLOAD':^{VARIABLE_WIDTH}}{Color.RESET} : {payload:<{VALUE_WIDTH}} ║")
        print(f"╠{'═' * VARIABLE_FRAME_WIDTH}╩{'═' * VALUE_FRAME_WIDTH}╣")
        print(f"║{Color.BRIGHT_CYAN}{f'HELP':^{VARIABLE_FRAME_WIDTH}}{Color.RESET}║{' Type `help` to show available commands.':<{VALUE_FRAME_WIDTH}}║")
        print(f"╚{'═' * VARIABLE_FRAME_WIDTH}═{'═' * VALUE_FRAME_WIDTH}╝")

    def _prepare_payload(self, payload: str) -> None:
        """
        Prepares the selected payload and handles user interactions in a loop until 'exit' is selected.

        Args:
            payload (str): The selected payload's path.

        Function Details:
            - Loads the payload variables.
            - Checks if the payload file is valid.
            - Displays the preparation menu.
            - Handles user commands like 'set', 'back', 'generate' and 'exit'.
        """
        while True:
            variables: list[str] = self._extract_placeholders(payload)
            if len(variables) == 0:
                exit(
                    log_level=LogLevel.ERROR, 
                    text=f"Payload ({payload}) is not in the appropriate format."
                )

            self._load_variables(variables)
            if not self._check_payload(payload):
                exit(
                    log_level=LogLevel.ERROR, 
                    text=f"Payload ({payload}) is missing or access is blocked."
                )

            self._preparation_menu(payload, variables)

            print(UPPER_FLAG)
            option: str = input(DOWN_FLAG)
            match option.lower():
                case option if option.lower().startswith("set ") and any(option.lower().startswith(f"set {variable.lower()}") for variable in variables):
                    for variable in variables:
                        if option.startswith(f"set {variable.lower()}"):
                            setattr(self, variable.lower(), option.removeprefix(f"set {variable.lower()}").strip())
                            break

                case option if option.lower().strip() == "generate":
                    payload_name: str = self._validate_input(
                        prompt=f"{Color.BRIGHT_GREEN}{LogLevel.SUCCESS}{Color.RESET} Enter the name for payload: ",
                        condition=lambda x: len(x) > 0,
                        failure_message="Payload name must contain at least one character."
                    ).strip()

                    payload_icon: str = self._validate_input(
                        prompt=f"{Color.BRIGHT_GREEN}{LogLevel.SUCCESS}{Color.RESET} Enter the icon for payload (optional): ",
                        condition=lambda x: x == "" or os.path.exists(x),
                        failure_message="Payload icon file not found in specified path."
                    ).strip()

                    payload_path: str = self._validate_input(
                        prompt=f"{Color.BRIGHT_GREEN}{LogLevel.SUCCESS}{Color.RESET} Enter the path for payload (optional): ",
                        condition=lambda x: x == "" or (os.path.exists(x) and os.path.isdir(x)),
                        failure_message="Payload path invalid or specified directory missing."
                    ).strip()

                    self._generate_payload(
                        payload_source=payload,
                        payload_name=payload_name,
                        payload_icon=payload_icon,
                        payload_path=payload_path,
                        payload_variables={variable: getattr(self, variable.lower()) for variable in variables}
                    )
                    break

                case option if option.lower().strip() == "help":
                    self._help_prepare()
                    continue

                case option if option.lower().strip() == "back":
                    getattr(importlib.import_module('Morphius'), "Morphius")().main()
                    break

                case option if option.lower().strip() == "exit":
                    exit(
                        log_level=LogLevel.NOTICE,
                        text=f"Signed out of {TOOL_NAME}."
                    )

                case _:
                    log_message(
                        log_level=LogLevel.WARNING, 
                        text="Please enter a valid input."
                    )
                    time.sleep(1.25)
                    continue
