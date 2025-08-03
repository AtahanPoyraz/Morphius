[![Tool Version](https://img.shields.io/badge/Tool%20Version-1.0.0-green.svg)](https://github.com/AtahanPoyraz/Morphius) [![Python Version](https://img.shields.io/badge/Python-3.12%2B-yellow.svg)](https://www.python.org/) [![GPLv3 License](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://opensource.org/license/gpl-3-0)

# **Morphius**
## **Introduction**
The Morphius project is designed to manipulate, obfuscate, and convert Python scripts into executable files, enabling the creation of secure and stealthy payloads. It allows users to easily modify various payload types and generate executables for targeted systems, providing flexibility and efficiency in payload delivery.

### **Supported Operating Systems**
* `Debian 12+`
* `Windows 10+`

### **Requirements:**
* `Python 3.12+`

### **The project has the following basic functionalities:**
#### __Script Manipulation:__
The core functionality in Morphius project is to manipulate and customize Python files with placeholders received from the user. This process starts by analyzing the descriptions, libraries used and placeholders in the payload files. Then, the content of the file is dynamically modified with the values provided by the user.

* __Variables Management:__ The placeholders in the payload files are defined in **`${VARIABLE_NAME}`** format and these placeholders are first extracted from the file. This is done with RegEx and only unique placeholders are stored in a list. Then, these placeholders are loaded as properties of the class so that each placeholder can be easily customized with a user input or predefined value.

* __Extracting Remarks:__ The comments in the payload file start with **`#//`** and these lines are extracted from the file and shown to the user. This provides quick access to information explaining what the payload file is used for.

* __Library Detection:__ The libraries used in the payload are identified by **`import`** and **`from ... import`**. This makes it possible to see which external libraries the payload depends on and includes them in the executable.

* __Dynamic File Authoring:__ The content of the payload file is customized with specified placeholders and values. During this process, the placeholder of each variable is replaced with the value provided by the user. As a result, a completely new and customized payload file is created and saved in the **`dist/generate/`** directory.

These functions allow you to manipulate and customize Python files in your Morphius project. With input from the user, each payload file can be customized into the desired shape and produced as output. This process represents a powerful structure for file handling, error checking and dynamic content creation.

#### __Script Obfuscation:__
* PyArmor is used in the Morphius project to increase the security of Python payload files and make reverse engineering more difficult. The `_obfuscate_payload` method takes the payload file specified by the user and obfuscates it using the PyArmor command line tool. This process preserves the source code in the payload file, while making the code harder to understand to prevent outside interference. The obfuscated file is saved in the **`dist/obfuscate/`** directory.

* PyArmor analyzes the comments, variables and functions in the Python file and obfuscates them, securing them without breaking the original structure. If an error occurs during the obfuscation process, the process is stopped and the user is notified by logging the error message. This makes it difficult to interfere with the original payload file.

#### __Script Compilation:__
* Using PyInstaller, the process of converting the Python payload file into a standalone executable is an important part of the Morphius project. The **`_build_payload`** function takes the Python payload file customized and obfuscated in the previous steps, then uses PyInstaller to turn it into a single executable (EXE). This process allows the payload to run fully standalone, with external libraries and necessary files.

* After successful compilation, the payload becomes a standalone executable file and is saved in the specified directory. If **`payload_path`** is not specified, the compiled file will be saved in the **`dist/`** directory. If an error occurs, the process is aborted and the error message is logged and reported to the user.

* This process is a powerful step in ensuring that your Python application can run independently, making it possible for the payload to run anywhere.

## Installation and Setup
### **1- Installation**
To get started, clone the Morphius repository to your local machine using the commands below:
```bash
git clone https://github.com/AtahanPoyraz/Morphius.git
cd Morphius
```

### **2- Install Dependencies**
Install all the necessary packages and dependencies with the command below:
```bash
pip3 install -r requirements.txt
```

### **3- Run the Morphius**
```bash
python3 Morphius.py
```

## **Summary**
The Morphius is a versatile tool that helps customize, obfuscate, and compile Python scripts into standalone executable files. It’s designed to give users control over their payloads, making them flexible and easy to adapt for different needs.

__Important:__ This tool is made for learning, research, and ethical purposes only. Any harmful or illegal use is strictly discouraged and the responsibility belongs to the user.


## **Authors**

- [@AtahanPoyraz](https://github.com/AtahanPoyraz)
