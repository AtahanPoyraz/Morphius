# .PHONY targets that do not correspond to actual files
.PHONY: help run install uninstall clean reinstall info

# Default goal
.DEFAULT_GOAL := run

# Display help message with all targets
help:
	@echo "Makefile commands:"
	@echo "  run       - Run the main.py script"
	@echo "  install   - Install project dependencies"
	@echo "  uninstall - Uninstall project dependencies"
	@echo "  clean     - Clean up pyc files and build directories"
	@echo "  reinstall - Reinstall dependencies after cleaning"
	@echo "  info      - Show system info (Python & pip version)"
	@echo "  help      - Show this help message"

# Run the main script
run:
	@echo "Running the main script..."
	python3 -u main.py

# Install project dependencies
install:
	@echo "Installing project dependencies..."
	pip3 install -r requirements.txt

# Uninstall project dependencies
uninstall:
	@echo "Uninstalling project dependencies..."
	pip3 uninstall -r requirements.txt -y

# Clean up pyc files and other generated files
clean:
	@echo "Cleaning up pyc files and build directories..."
	# Remove pyc files and __pycache__ directories
	find . -type f -name "*.pyc" -exec rm -f {} \;
	find . -type d -name "__pycache__" -exec rm -rf {} \;
	# Remove logs
	find . -type f -name "*.log" -exec rm -f {} \;
	# Remove build and dist directories
	rm -rf dist/ build/

# Reinstall dependencies, helpful after `requirements.txt` changes
reinstall: clean uninstall install
	@echo "Dependencies reinstalled successfully."

# Show system info (Python version, pip version, etc.)
info:
	@echo "Python version:"
	python3 --version
	@echo "pip version:"
	pip3 --version
