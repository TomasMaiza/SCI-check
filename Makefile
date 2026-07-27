BINDINGS_BUILD_DIR = src/bindings/build
PYTHON_DIR = src/coverage_checker

.PHONY: all compile clean run test

all: compile

compile:
	@mkdir -p $(BINDINGS_BUILD_DIR)
	@cd $(BINDINGS_BUILD_DIR) && cmake .. && $(MAKE)

run: compile
	@PYTHONPATH=./src python3 test/testc2.py

subregions: compile
	@PYTHONPATH=.:./src pytest test/test_subregions.py -v

clean:
	@rm -rf $(BINDINGS_BUILD_DIR)
	@rm -f $(PYTHON_DIR)/pyattene*.so
	@find . -type d -name "__pycache__" -exec rm -rf {} +