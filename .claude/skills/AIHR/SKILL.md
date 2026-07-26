```markdown
# AIHR Development Patterns

> Auto-generated skill from repository analysis

## Overview
This skill teaches you the core development patterns and conventions used in the AIHR Python codebase. You'll learn how to structure files, write imports and exports, follow commit message conventions, and organize tests. These patterns ensure consistency, readability, and maintainability across the project.

## Coding Conventions

### File Naming
- Use **snake_case** for all file names.
  - Example: `data_processor.py`, `user_service.py`

### Import Style
- Use **alias imports** to clarify module usage.
  - Example:
    ```python
    import numpy as np
    import pandas as pd
    ```

### Export Style
- Use **named exports** to control what is exposed from each module.
  - Example:
    ```python
    __all__ = ['process_data', 'User']
    ```

### Commit Messages
- Follow the **conventional commits** format.
- Use the `feat` prefix for new features.
  - Example:
    ```
    feat: add user authentication module
    ```

## Workflows

### Adding a New Feature
**Trigger:** When implementing a new feature or module  
**Command:** `/add-feature`

1. Create a new Python file using snake_case naming.
2. Implement the feature, using alias imports for dependencies.
3. Define `__all__` to specify exported functions/classes.
4. Write corresponding test files (see Testing Patterns).
5. Commit changes with a message like:  
   `feat: [short description of the feature]`

### Refactoring Code
**Trigger:** When improving or restructuring existing code  
**Command:** `/refactor-code`

1. Identify the code to refactor.
2. Update file and variable names to follow snake_case.
3. Ensure all imports use aliases where appropriate.
4. Update `__all__` as needed.
5. Run tests to verify changes.
6. Commit with a message like:  
   `feat: refactor [module or function name] for clarity`

## Testing Patterns

- Test files follow the `*.test.*` pattern (e.g., `user_service.test.py`).
- The specific testing framework is not specified; use standard Python testing practices.
- Place tests alongside or near the modules they cover.
- Example test file:
  ```python
  # user_service.test.py
  import pytest
  from user_service import User

  def test_user_creation():
      user = User('Alice')
      assert user.name == 'Alice'
  ```

## Commands
| Command         | Purpose                                  |
|-----------------|------------------------------------------|
| /add-feature    | Start workflow for adding a new feature  |
| /refactor-code  | Start workflow for refactoring code      |
```
