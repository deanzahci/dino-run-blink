# Dino Run Blink - Agent Guidelines

## Build/Lint/Test Commands

### Testing

- Run all tests: `uv run python tests/test_config_and_utils.py`
- Run single test: `uv run python -m unittest tests.test_config_and_utils.TestClass.test_method`
- No linting tools configured

## Code Style Guidelines

### Imports

- Standard library first, third-party second, local last
- Absolute imports for local modules
- Group imports with blank lines

### Naming

- Constants: `ALL_CAPS_WITH_UNDERSCORES`
- Functions/variables: `snake_case`
- Classes: `PascalCase`

### Types & Documentation

- Use type hints where beneficial
- Include docstrings for public functions/classes (Google/NumPy style)
- Docstrings: description, Args, Returns, Raises

### Error Handling

- Assertions for config validation
- Log errors with appropriate levels
- Handle exceptions gracefully with try/except
- Exit on critical failures (SystemExit)

### Code Structure

- Constants at module level with comments
- Separate concerns: config, utils, main logic, plotting
- Meaningful variable names, single responsibility functions

### Formatting

- 4-space indentation
- Consistent spacing around operators
- Blank lines between logical sections</content>
  <parameter name="filePath">/Users/koichi/Projects/dino-run-blink/AGENTS.md
