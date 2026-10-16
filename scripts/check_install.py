"""Check local dependencies; optionally exercise a short GUI event loop."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gui", action="store_true", help="Create a window for 0.5 seconds")
    args = parser.parse_args()
    try:
        import tkinter
        import PIL
        from src.gui import ImageRenameApp

        print(f"Python: {sys.version.split()[0]}")
        print(f"Pillow: {PIL.__version__}")
        print(f"Tk: {tkinter.TkVersion}")
        if args.gui:
            app = ImageRenameApp()
            # Installation checks must not read or prompt for a user's session.
            app._offer_resume_from_known_locations = lambda: None
            app.after(500, app.destroy)
            app.mainloop()
            print("GUI startup: OK")
        print("Installation check: OK")
        return 0
    except Exception as exc:
        print(f"Installation check failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
