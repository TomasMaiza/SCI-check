BINDINGS_BUILD_DIR = bindings/build
PYTHON_DIR = coverage_checker

.PHONY: all compile clean run test

all: compile

compile:
	@mkdir -p $(BINDINGS_BUILD_DIR)
	@cd $(BINDINGS_BUILD_DIR) && cmake .. && $(MAKE)

run: compile
	@python3 test/testc2.py

clean:
	@rm -rf $(BINDINGS_BUILD_DIR)
	@rm -f $(PYTHON_DIR)/pyattene*.so
	@find . -type d -name "__pycache__" -exec rm -rf {} +