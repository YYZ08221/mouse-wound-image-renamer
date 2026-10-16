import csv
import json
import shutil
from datetime import datetime
from pathlib import Path


LOG_FIELDS = [
    "index",
    "original_path",
    "original_name",
    "new_name",
    "output_path",
    "action",
    "timestamp",
    "status",
    "note",
]


class RenameManager:
    def __init__(self, output_folder):
        self.output_folder = Path(output_folder)
        self.output_folder.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_path = self.output_folder / f"rename_log_{timestamp}.csv"
        self.session_path = self.output_folder / "session_state.json"
        self._ensure_log()

    def _ensure_log(self):
        if not self.log_path.exists():
            with self.log_path.open("w", encoding="utf-8-sig", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=LOG_FIELDS)
                writer.writeheader()

    def log(self, index, original_path, new_name, output_path, action, status="ok", note=""):
        original = Path(original_path) if original_path else Path("")
        row = {
            "index": index,
            "original_path": str(original_path),
            "original_name": original.name,
            "new_name": new_name,
            "output_path": str(output_path),
            "action": action,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "status": status,
            "note": note,
        }
        with self.log_path.open("a", encoding="utf-8-sig", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=LOG_FIELDS)
            writer.writerow(row)

    def save_copy(self, source_path, target_name):
        self.output_folder.mkdir(parents=True, exist_ok=True)
        destination = self.output_folder / target_name
        if destination.exists():
            raise FileExistsError(str(destination))
        shutil.copy2(source_path, destination)
        return destination

    def make_unique_path(self, target_name):
        base = Path(target_name).stem
        suffix = Path(target_name).suffix
        candidate = self.output_folder / target_name
        counter = 1
        while candidate.exists():
            candidate = self.output_folder / f"{base}_{counter:03d}{suffix}"
            counter += 1
        return candidate

    def undo_file(self, path):
        target = Path(path)
        if target.exists():
            target.unlink()
            return True
        return False

    def save_session(self, state):
        self.output_folder.mkdir(parents=True, exist_ok=True)
        temp_path = self.session_path.with_suffix(".json.tmp")
        temp_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
        temp_path.replace(self.session_path)

    @staticmethod
    def load_session(path):
        session_path = Path(path)
        if not session_path.exists():
            return None
        with session_path.open("r", encoding="utf-8") as file:
            return json.load(file)
