# Dino Run Blink - Agent Guidelines

## Build/Lint/Test Commands

### Testing

- Run all tests: `uv run python tests/test_config_and_utils.py`
- Run single test: `uv run python -m unittest tests.test_config_and_utils.TestClass.test_method`
- No dedicated test runner configured (uses Python's unittest directly)

### Linting/Formatting

- No linting tools configured (ruff, black, mypy, flake8 not found)
- No build commands configured

## Code Style Guidelines

### Imports

- Standard library imports first
- Third-party imports second
- Local imports last
- Use absolute imports for local modules
- Group imports with blank lines between groups

### Naming Conventions

- Constants: `ALL_CAPS_WITH_UNDERSCORES`
- Functions/variables: `snake_case`
- Classes: `PascalCase`
- Modules: `snake_case`

### Types and Documentation

- Use type hints where beneficial
- Include docstrings for all public functions and classes
- Docstrings follow Google/NumPy style with description, args, returns, raises

### Error Handling

- Use assertions for configuration validation
- Log errors with appropriate levels (INFO, ERROR)
- Handle exceptions gracefully with try/except blocks
- Exit program on critical failures (SystemExit)

### Code Structure

- Constants defined at module level with clear comments
- Validation functions to ensure configuration integrity
- Separate concerns: config, utils, main logic, plotting
- Use meaningful variable names
- Keep functions focused on single responsibilities

### Formatting

- 4-space indentation
- Line length: reasonable (no strict limit enforced)
- Consistent spacing around operators
- No trailing commas
- Blank lines between logical sections</content>
  <parameter name="filePath">/Users/koichi/Projects/dino-run-blink/AGENTS.md

