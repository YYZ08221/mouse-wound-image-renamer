import json
import os
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageTk, UnidentifiedImageError

from .image_loader import get_image_files
from .rename_manager import RenameManager
from .utils import build_target_name, has_illegal_chars, safe_int


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LAST_SESSION_HINT = PROJECT_ROOT / "logs" / "last_session.json"


class ImageRenameApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("图片批量重命名工具")
        self.geometry("1100x760")
        self.minsize(860, 620)

        self.input_folder = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.new_name = tk.StringVar()
        self.status_text = tk.StringVar(value="请选择输入文件夹和输出文件夹")
        self.progress_text = tk.StringVar(value="第 0 / 0 张")
        self.original_name_text = tk.StringVar(value="当前原始文件名：")
        self.auto_mode = tk.BooleanVar(value=False)
        self.auto_prefix = tk.StringVar(value="image_")
        self.auto_start = tk.StringVar(value="1")
        self.auto_digits = tk.StringVar(value="3")

        self.files = []
        self.current_index = 0
        self.manager = None
        self.saved_records = []
        self.skipped_files = []
        self.processed_files = []
        self.input_cache = {}
        self.current_photo = None
        self.current_image = None
        self.resize_job = None
        self.last_output_folder = None

        self._build_ui()
        self._bind_shortcuts()
        self.after(300, self._offer_resume_from_known_locations)

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        top = ttk.Frame(self, padding=10)
        top.grid(row=0, column=0, sticky="ew")
        top.columnconfigure(1, weight=1)
        top.columnconfigure(3, weight=1)

        ttk.Button(top, text="选择输入文件夹", command=self.choose_input).grid(row=0, column=0, padx=(0, 6))
        ttk.Label(top, textvariable=self.input_folder).grid(row=0, column=1, sticky="ew", padx=(0, 12))
        ttk.Button(top, text="选择输出文件夹", command=self.choose_output).grid(row=0, column=2, padx=(0, 6))
        ttk.Label(top, textvariable=self.output_folder).grid(row=0, column=3, sticky="ew", padx=(0, 12))
        ttk.Button(top, text="开始", command=self.start).grid(row=0, column=4)

        center = ttk.Frame(self, padding=(10, 0, 10, 8))
        center.grid(row=1, column=0, sticky="nsew")
        center.rowconfigure(0, weight=1)
        center.columnconfigure(0, weight=1)
        self.image_label = ttk.Label(center, anchor="center")
        self.image_label.grid(row=0, column=0, sticky="nsew")
        self.image_label.bind("<Configure>", self._on_image_area_resize)

        bottom = ttk.Frame(self, padding=10)
        bottom.grid(row=2, column=0, sticky="ew")
        bottom.columnconfigure(1, weight=1)

        ttk.Label(bottom, textvariable=self.progress_text).grid(row=0, column=0, sticky="w", padx=(0, 18))
        ttk.Label(bottom, textvariable=self.original_name_text).grid(row=0, column=1, sticky="ew", columnspan=5)

        ttk.Label(bottom, text="新文件名").grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.name_entry = ttk.Entry(bottom, textvariable=self.new_name)
        self.name_entry.grid(row=1, column=1, sticky="ew", pady=(8, 0), padx=(0, 8))
        ttk.Button(bottom, text="保存并下一张", command=self.save_and_next).grid(row=1, column=2, padx=4, pady=(8, 0))
        ttk.Button(bottom, text="跳过", command=self.skip_current).grid(row=1, column=3, padx=4, pady=(8, 0))
        ttk.Button(bottom, text="上一张", command=self.previous_image).grid(row=1, column=4, padx=4, pady=(8, 0))
        ttk.Button(bottom, text="撤销上一次保存", command=self.undo_last_save).grid(row=1, column=5, padx=4, pady=(8, 0))
        ttk.Button(bottom, text="打开输出文件夹", command=self.open_output_folder).grid(row=1, column=6, padx=(4, 0), pady=(8, 0))

        auto = ttk.LabelFrame(bottom, text="自动编号模式", padding=8)
        auto.grid(row=2, column=0, columnspan=7, sticky="ew", pady=(10, 0))
        auto.columnconfigure(5, weight=1)
        ttk.Checkbutton(auto, text="启用", variable=self.auto_mode, command=self._update_auto_preview).grid(row=0, column=0, padx=(0, 12))
        ttk.Label(auto, text="前缀").grid(row=0, column=1)
        ttk.Entry(auto, width=16, textvariable=self.auto_prefix).grid(row=0, column=2, padx=(4, 12))
        ttk.Label(auto, text="起始编号").grid(row=0, column=3)
        ttk.Entry(auto, width=8, textvariable=self.auto_start).grid(row=0, column=4, padx=(4, 12))
        ttk.Label(auto, text="位数").grid(row=0, column=5, sticky="w")
        ttk.Entry(auto, width=8, textvariable=self.auto_digits).grid(row=0, column=6, padx=(4, 0))
        self.auto_prefix.trace_add("write", lambda *_: self._update_auto_preview())
        self.auto_start.trace_add("write", lambda *_: self._update_auto_preview())
        self.auto_digits.trace_add("write", lambda *_: self._update_auto_preview())

        status = ttk.Label(self, textvariable=self.status_text, relief=tk.SUNKEN, anchor="w", padding=(8, 4))
        status.grid(row=3, column=0, sticky="ew")

    def _bind_shortcuts(self):
        self.bind("<Return>", lambda _event: self.save_and_next())
        self.bind("<Control-s>", lambda _event: self.save_and_next())
        self.bind("<Control-S>", lambda _event: self.save_and_next())
        self.bind("<Control-z>", lambda _event: self.undo_last_save())
        self.bind("<Control-Z>", lambda _event: self.undo_last_save())
        self.bind("<Left>", lambda _event: self.previous_image())
        self.bind("<Right>", lambda _event: self.skip_current())
        self.bind("<Escape>", lambda _event: self.new_name.set(""))

    def choose_input(self):
        folder = filedialog.askdirectory(title="选择输入文件夹")
        if folder:
            self.input_folder.set(folder)
            self.status_text.set("已选择输入文件夹")

    def choose_output(self):
        folder = filedialog.askdirectory(title="选择输出文件夹")
        if folder:
            self.output_folder.set(folder)
            self.last_output_folder = folder
            self.status_text.set("已选择输出文件夹")
            self._offer_resume_for_output(Path(folder))

    def start(self):
        input_folder = self.input_folder.get().strip()
        output_folder = self.output_folder.get().strip()
        if not input_folder:
            self._error("没有选择输入文件夹")
            return
        if not output_folder:
            self._error("没有选择输出文件夹")
            return
        input_path = Path(input_folder)
        output_path = Path(output_folder)
        if not input_path.exists() or not input_path.is_dir():
            self._error("输入文件夹不存在")
            return
        try:
            output_path.mkdir(parents=True, exist_ok=True)
            probe = output_path / ".write_test.tmp"
            probe.write_text("ok", encoding="utf-8")
            probe.unlink()
        except OSError as exc:
            self._error(f"输出文件夹没有写入权限：{exc}")
            return

        self.files = get_image_files(input_path)
        if not self.files:
            self._error("输入文件夹中没有支持的图片")
            return
        self.manager = RenameManager(output_path)
        self.current_index = min(self.current_index, len(self.files) - 1)
        self.status_text.set(f"已读取 {len(self.files)} 张图片")
        self._show_current_image()
        self._save_session()

    def _show_current_image(self):
        if not self.files:
            self.progress_text.set("第 0 / 0 张")
            self.original_name_text.set("当前原始文件名：")
            self.image_label.configure(image="", text="请选择文件夹并点击开始")
            return
        if self.current_index >= len(self.files):
            self._finish_all()
            return

        path = self.files[self.current_index]
        self.progress_text.set(f"第 {self.current_index + 1} / {len(self.files)} 张")
        self.original_name_text.set(f"当前原始文件名：{path.name}")
        self.new_name.set(self.input_cache.get(str(path), ""))
        self._update_auto_preview()
        try:
            with Image.open(path) as image:
                self.current_image = image.copy()
            self._render_current_image()
            self.status_text.set(f"正在处理：{path.name}")
            self.name_entry.focus_set()
        except (OSError, UnidentifiedImageError) as exc:
            self.current_image = None
            self.image_label.configure(image="", text="图片无法打开或已损坏")
            self._error(f"图片无法打开或损坏：{path.name}；{exc}", popup=False)

    def _render_current_image(self):
        if self.current_image is None:
            return
        width = max(1, self.image_label.winfo_width() - 20)
        height = max(1, self.image_label.winfo_height() - 20)
        image = self.current_image.copy()
        image.thumbnail((width, height), Image.Resampling.LANCZOS)
        self.current_photo = ImageTk.PhotoImage(image)
        self.image_label.configure(image=self.current_photo, text="")

    def _on_image_area_resize(self, _event):
        if self.resize_job:
            self.after_cancel(self.resize_job)
        self.resize_job = self.after(120, self._render_current_image)

    def save_and_next(self):
        if not self._ready_for_action():
            return
        source = self.files[self.current_index]
        if self.current_image is None:
            self._error("当前图片无法打开，不能保存")
            return
        try:
            target_name = self._current_target_name(source)
        except ValueError as exc:
            self._error(str(exc))
            return

        destination = self.manager.output_folder / target_name
        if destination.exists():
            self._handle_existing_file(target_name)
            return
        self._save_current_as(target_name)

    def _save_current_as(self, target_name):
        source = self.files[self.current_index]
        try:
            destination = self.manager.save_copy(source, target_name)
        except FileExistsError:
            self._handle_existing_file(target_name)
            return
        except OSError as exc:
            self._error(f"保存失败：{exc}")
            return

        typed_name = self.new_name.get()
        record = {
            "index": self.current_index,
            "original_path": str(source),
            "typed_name": typed_name,
            "new_name": destination.name,
            "output_path": str(destination),
        }
        self.saved_records.append(record)
        self.processed_files.append(str(source))
        self.manager.log(self.current_index, source, destination.name, destination, "saved")
        self.status_text.set(f"已保存为 {destination.name}")
        self.current_index += 1
        self._show_current_image()
        self._save_session()

    def _handle_existing_file(self, target_name):
        choice = messagebox.askyesnocancel(
            "输出文件已存在",
            f"{target_name} 已存在。\n\n是：自动追加编号\n否：重新输入文件名\n取消：跳过当前图片",
        )
        if choice is True:
            unique = self.manager.make_unique_path(target_name)
            self._save_current_as(unique.name)
        elif choice is False:
            self.status_text.set("输出文件已存在，请重新输入文件名")
            self.name_entry.focus_set()
        else:
            self.skip_current()

    def skip_current(self):
        if not self._ready_for_action(allow_manager_missing=True):
            return
        if self.current_index >= len(self.files):
            return
        source = self.files[self.current_index]
        self.input_cache[str(source)] = self.new_name.get()
        self.skipped_files.append(str(source))
        self.processed_files.append(str(source))
        if self.manager:
            self.manager.log(self.current_index, source, "", "", "skipped", note="用户跳过")
        self.status_text.set(f"已跳过 {source.name}")
        self.current_index += 1
        self._show_current_image()
        self._save_session()

    def previous_image(self):
        if not self.files:
            return
        if self.current_index <= 0:
            self.status_text.set("已经是第一张")
            return
        if self.current_index < len(self.files):
            self.input_cache[str(self.files[self.current_index])] = self.new_name.get()
        self.current_index -= 1
        self._show_current_image()
        self._save_session()

    def undo_last_save(self):
        if not self.saved_records:
            self.status_text.set("没有可撤销的保存记录")
            return
        record = self.saved_records.pop()
        existed = True
        if self.manager:
            existed = self.manager.undo_file(record["output_path"])
            self.manager.log(
                record["index"],
                record["original_path"],
                record["new_name"],
                record["output_path"],
                "undone",
                status="ok" if existed else "missing",
                note="撤销保存" if existed else "目标文件不存在，已仅回退进度",
            )
        self.current_index = min(record["index"], len(self.files) - 1)
        self.input_cache[record["original_path"]] = record.get("typed_name", "")
        if record["original_path"] in self.processed_files:
            self.processed_files.remove(record["original_path"])
        self._show_current_image()
        if existed:
            self.status_text.set("已撤销上一次保存")
        else:
            self.status_text.set("目标文件不存在，已仅回退进度")
        self._save_session()

    def open_output_folder(self):
        folder = self.output_folder.get().strip()
        if not folder:
            self._error("没有选择输出文件夹")
            return
        path = Path(folder)
        if not path.exists():
            self._error("输出文件夹不存在")
            return
        os.startfile(path)

    def _current_target_name(self, source):
        if self.auto_mode.get():
            prefix = self.auto_prefix.get().strip()
            if not prefix:
                raise ValueError("自动编号前缀不能为空")
            if has_illegal_chars(prefix):
                raise ValueError("自动编号前缀包含非法字符")
            start = safe_int(self.auto_start.get(), 1, 0)
            digits = safe_int(self.auto_digits.get(), 3, 1)
            number = start + self.current_index
            return f"{prefix}{number:0{digits}d}{source.suffix}"
        return build_target_name(self.new_name.get(), source.suffix)

    def _update_auto_preview(self):
        if not self.auto_mode.get() or not self.files or self.current_index >= len(self.files):
            return
        try:
            self.new_name.set(self._current_target_name(self.files[self.current_index]))
        except ValueError:
            pass

    def _finish_all(self):
        self.progress_text.set(f"第 {len(self.files)} / {len(self.files)} 张")
        self.original_name_text.set("当前原始文件名：全部完成")
        self.image_label.configure(image="", text="全部完成")
        self.status_text.set("全部完成")
        self._save_session()
        messagebox.showinfo("完成", "全部完成。")

    def _ready_for_action(self, allow_manager_missing=False):
        if not self.files:
            self._error("请先选择文件夹并点击开始")
            return False
        if self.current_index >= len(self.files):
            self.status_text.set("全部完成")
            return False
        if not allow_manager_missing and self.manager is None:
            self._error("请先点击开始")
            return False
        return True

    def _save_session(self):
        if not self.manager:
            return
        state = {
            "input_folder": self.input_folder.get(),
            "output_folder": self.output_folder.get(),
            "current_index": self.current_index,
            "processed_files": self.processed_files,
            "skipped_files": self.skipped_files,
            "saved_records": self.saved_records,
            "input_cache": self.input_cache,
        }
        try:
            self.manager.save_session(state)
            LAST_SESSION_HINT.parent.mkdir(parents=True, exist_ok=True)
            hint = {"session_path": str(self.manager.session_path)}
            LAST_SESSION_HINT.write_text(json.dumps(hint, ensure_ascii=False, indent=2), encoding="utf-8")
        except OSError as exc:
            self.status_text.set(f"会话记录保存失败：{exc}")

    def _offer_resume_from_known_locations(self):
        if self.output_folder.get():
            self._offer_resume_for_output(Path(self.output_folder.get()))
            return
        if not LAST_SESSION_HINT.exists():
            return
        try:
            hint = json.loads(LAST_SESSION_HINT.read_text(encoding="utf-8"))
            session_path = Path(hint.get("session_path", ""))
        except (OSError, ValueError) as exc:
            self.status_text.set(f"最近会话记录损坏：{exc}")
            return
        if session_path.name == "session_state.json" and session_path.exists():
            self._offer_resume_for_output(session_path.parent)

    def _offer_resume_for_output(self, output_path):
        session_path = output_path / "session_state.json"
        if not session_path.exists():
            return
        try:
            state = RenameManager.load_session(session_path)
        except (OSError, ValueError) as exc:
            self.status_text.set(f"会话记录损坏：{exc}")
            messagebox.showwarning("会话记录损坏", f"无法读取上次会话：{exc}")
            return
        if not state:
            return
        should_resume = messagebox.askyesno("继续上次进度", "发现上次会话记录，是否继续上次进度？")
        if should_resume:
            self._restore_session(state)

    def _restore_session(self, state):
        self.input_folder.set(state.get("input_folder", ""))
        self.output_folder.set(state.get("output_folder", ""))
        self.current_index = safe_int(state.get("current_index"), 0, 0)
        self.processed_files = list(state.get("processed_files", []))
        self.skipped_files = list(state.get("skipped_files", []))
        self.saved_records = list(state.get("saved_records", []))
        self.input_cache = dict(state.get("input_cache", {}))
        output = self.output_folder.get()
        if output:
            self.manager = RenameManager(output)
        input_path = self.input_folder.get()
        if input_path:
            self.files = get_image_files(input_path)
        if self.files:
            self.current_index = min(self.current_index, len(self.files) - 1)
            self._show_current_image()
            self.status_text.set("已继续上次进度")
        else:
            self.status_text.set("已读取会话，但输入文件夹中没有图片")

    def _error(self, message, popup=True):
        self.status_text.set(message)
        if popup:
            messagebox.showerror("错误", message)


def run_app():
    app = ImageRenameApp()
    app.mainloop()


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    run_app()
