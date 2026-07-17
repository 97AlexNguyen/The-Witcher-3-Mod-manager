# Repository Working Instructions

## Python environment

- Always use the Conda environment named `w3_manager` for Python commands in this repository.
- Prefer `conda run -n w3_manager <command>` so commands use the correct environment even when the current shell has not activated it.
- Run the application with:

  ```powershell
  conda run -n w3_manager python main.py
  ```

- Run Python verification with the same environment, for example:

  ```powershell
  conda run -n w3_manager python -m py_compile main.py
  conda run -n w3_manager python -m pytest
  ```

- For headless Qt smoke tests, set `QT_QPA_PLATFORM=offscreen` for the command executed inside `w3_manager`.
- Do not install Python packages into the system Python or another Conda environment for this project.


# note :
- Luôn dùng tiếng anh trong code, không dùng tiếng việt

