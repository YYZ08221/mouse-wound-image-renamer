# Agent Guide

## Purpose and scope

Windows tkinter/Pillow GUI for preparing mouse wound-study photographs: visual
review, consistent filenames, copy to output, audit logs, and session recovery.
The current code does not detect wounds, segment images, measure area, calculate
closure rates, train models, or call an AI API. Describe only implemented features.

## Install

Read README.md and docs/AGENT_INSTALL.md first. Use an isolated .venv and a real
Python executable with tkinter. On Windows run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -GuiCheck
```

ExecutionPolicy Bypass here applies only to this process. Do not change the
machine-wide execution policy. Use `-Python 'C:\path\to\python.exe'` if needed.
Omit -GuiCheck on machines without an interactive desktop and report that GUI
startup has not been verified. GUI operation requires a Windows desktop session.

## Verify and run

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe scripts/check_install.py --gui
.\.venv\Scripts\python.exe main.py
```

Run these commands from the repository root. Do not run install.ps1 -Launch
inside an unattended blocking job; run checks first, then launch for the user.

## Data and code boundaries

- main.py starts the UI; src/gui.py handles interaction.
- src/image_loader.py lists top-level images in natural filename order.
- src/rename_manager.py handles copies, logs, undo deletion, and sessions.
- src/utils.py contains naming utilities; tests/test_core.py covers core behavior.
- Keep raw data outside this repository. Never commit study photographs, local
  paths/session files, logs, .venv, credentials, or backup contents.
- Preserve source images and metadata; keep default copying and no-overwrite behavior.
- Filename changes do not transcode pixels. Preserve the source extension for
  research workflows even though the UI accepts other supported extensions.
- Require explicit study metadata from the researcher. Do not infer mouse ID,
  experimental group, day, or wound measurements from a photograph.
- Use synthetic temporary files when testing; do not operate on real datasets.
