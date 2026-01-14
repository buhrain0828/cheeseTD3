CheeseTD3
==========

Quick start
-----------

- Open PowerShell and change to the project folder:

```powershell
cd C:\Users\osabr\OneDrive\Documents\GitHub\cheeseTD3
```

- Activate the project venv (created for this workspace):

```powershell
.\.venv\Scripts\Activate.ps1
```

- Install dependencies (if needed):

```powershell
pip install -r main\requirements.txt
# or at minimum:
# pip install pygame
```

- Run the game from the project root (recommended):

```powershell
python main.py
```

- If you prefer running the script under `main/` directly, use the workspace venv python executable:

```powershell
C:/Users/osabr/OneDrive/Documents/GitHub/cheeseTD3/.venv/Scripts/python.exe main\main.py
```

Notes about imports
-------------------

- This project uses absolute imports like `assets.*`. Prefer running from the project root so imports resolve without modifying `sys.path`.
- There is a small `sys.path` insertion in `main/main.py` to allow running that file while inside the `main/` folder. If you convert the project into a package (add `__init__.py` files) this workaround won't be necessary.

VS Code
-------

- I added a workspace `/.vscode/launch.json` and `/.vscode/settings.json` that point VS Code to the workspace venv. If VS Code's Run/Start button doesn't behave as expected:
  - Open Command Palette → `Python: Select Interpreter` → choose the `.venv` at `C:\Users\osabr\OneDrive\Documents\GitHub\cheeseTD3\.venv\Scripts\python.exe`.
  - Use the Debug configuration named **"Python: Run main.py (venv)"** to run the game in the integrated terminal.

Troubleshooting
---------------

- If you see `ModuleNotFoundError: No module named 'assets'` when running from `main/`, run `python` from the project root or use the venv python path shown above.
- If the Pygame window closes but the process stays running, try running from a terminal and check that `pygame.quit()` and `sys.exit(0)` are executed. The repository includes these calls in `main.py`.
- To ensure image files load correctly, confirm `assets/images/enemies/foe1.png` exists. Missing files raise `pygame.error`.

Further improvements
--------------------

- Convert the repository into a package (add `__init__.py`) and remove the `sys.path` insertion.
- Add a short `CONTRIBUTING.md` and tests if you want CI.

Contact
-------

If you want, I can:
- Commit these workspace files and add a `.gitignore` entry for `.vscode`.
- Convert the repo into a proper package layout.
- Add a minimal `Makefile` or scripts for Windows and Unix runners.

Tell me which of those you'd like next.
