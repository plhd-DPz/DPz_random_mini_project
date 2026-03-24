"""
Code Template Generator
=======================
Ứng dụng desktop tự động tạo file code từ template,
phục vụ việc lưu bài tập lập trình.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os

# ─────────────────────────────────────────────
#  DỮ LIỆU TEMPLATE MẶC ĐỊNH
# ─────────────────────────────────────────────
DEFAULT_TEMPLATES = {
    "C": {
        "ext": ".c",
        "format": (
            "/*==========================================================\n"
            "{problem}\n"
            "==========================================================*/\n\n"
            "{solution}"
        ),
    },
    "C++": {
        "ext": ".cpp",
        "format": (
            "/*==================\n"
            "{problem}\n"
            "==================*/\n\n"
            "{solution}"
        ),
    },
    "Python": {
        "ext": ".py",
        "format": (
            '"""\n'
            "==================\n"
            "{problem}\n"
            "==================\n"
            '"""\n\n'
            "{solution}"
        ),
    },
    "Java": {
        "ext": ".java",
        "format": (
            "/*==================\n"
            "{problem}\n"
            "==================*/\n\n"
            "{solution}"
        ),
    },
}

# ─────────────────────────────────────────────
#  BẢNG MÀU & FONT (THEME)
# ─────────────────────────────────────────────
THEME = {
    "bg":           "#1E1E2E",   # nền chính (dark)
    "bg_panel":     "#252538",   # nền panel / frame
    "bg_input":     "#2A2A3F",   # nền ô nhập liệu
    "accent":       "#7C6AF7",   # tím chính
    "accent2":      "#5EEAD4",   # xanh lá nhạt
    "accent_hover": "#9580FF",   # tím sáng hơn khi hover
    "text":         "#CDD6F4",   # chữ chính
    "text_dim":     "#6C7086",   # chữ mờ / label phụ
    "success":      "#A6E3A1",   # xanh lá thành công
    "danger":       "#F38BA8",   # đỏ lỗi
    "border":       "#383851",   # viền
    "btn_fg":       "#FFFFFF",
}

FONT_MAIN   = ("Consolas", 10)
FONT_LABEL  = ("Segoe UI", 9, "bold")
FONT_TITLE  = ("Segoe UI", 13, "bold")
FONT_MONO   = ("Consolas", 10)
FONT_BTN    = ("Segoe UI", 9, "bold")


# ═══════════════════════════════════════════════════════
#  WIDGET TIỆN ÍCH
# ═══════════════════════════════════════════════════════

def styled_label(parent, text, **kw):
    """Label với style mặc định."""
    cfg = dict(
        text=text,
        bg=THEME["bg_panel"],
        fg=THEME["text"],
        font=FONT_LABEL,
        anchor="w",
    )
    cfg.update(kw)
    return tk.Label(parent, **cfg)


def styled_entry(parent, **kw):
    """Entry với style dark theme."""
    cfg = dict(
        bg=THEME["bg_input"],
        fg=THEME["text"],
        insertbackground=THEME["accent2"],
        relief="flat",
        font=FONT_MAIN,
        highlightthickness=1,
        highlightbackground=THEME["border"],
        highlightcolor=THEME["accent"],
    )
    cfg.update(kw)
    return tk.Entry(parent, **cfg)


def styled_text(parent, height=10, **kw):
    """Text widget có scrollbar dọc, dark theme."""
    frame = tk.Frame(
        parent,
        bg=THEME["border"],
        padx=1, pady=1,
    )

    cfg = dict(
        bg=THEME["bg_input"],
        fg=THEME["text"],
        insertbackground=THEME["accent2"],
        relief="flat",
        font=FONT_MONO,
        height=height,
        wrap="word",
        selectbackground=THEME["accent"],
        selectforeground=THEME["btn_fg"],
        undo=True,
    )
    cfg.update(kw)

    text_widget = tk.Text(frame, **cfg)
    scrollbar   = ttk.Scrollbar(frame, orient="vertical", command=text_widget.yview)
    text_widget.configure(yscrollcommand=scrollbar.set)

    text_widget.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    return frame, text_widget


def styled_button(parent, text, command, accent=True, width=18):
    """Button với hiệu ứng hover."""
    bg_normal = THEME["accent"] if accent else THEME["bg_panel"]
    bg_hover  = THEME["accent_hover"] if accent else THEME["border"]
    fg        = THEME["btn_fg"]

    btn = tk.Button(
        parent,
        text=text,
        command=command,
        bg=bg_normal,
        fg=fg,
        font=FONT_BTN,
        relief="flat",
        cursor="hand2",
        width=width,
        padx=10,
        pady=6,
        activebackground=bg_hover,
        activeforeground=fg,
        borderwidth=0,
    )

    def on_enter(_):
        btn.config(bg=bg_hover)

    def on_leave(_):
        btn.config(bg=bg_normal)

    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn


# ═══════════════════════════════════════════════════════
#  CỬA SỔ CHỈNH SỬA TEMPLATE
# ═══════════════════════════════════════════════════════

class EditTemplateWindow(tk.Toplevel):
    """Cửa sổ con cho phép xem & chỉnh sửa template theo từng ngôn ngữ."""

    def __init__(self, parent, templates: dict):
        super().__init__(parent)
        self.templates = templates          # tham chiếu dict gốc
        self.title("Edit Templates")
        self.configure(bg=THEME["bg"])
        self.resizable(True, True)
        self.geometry("620x520")
        self.minsize(500, 420)

        # Căn giữa màn hình
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width()  - 620) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 520) // 2
        self.geometry(f"+{x}+{y}")

        self._build_ui()
        self._load_language(self.lang_var.get())

    # ── xây dựng giao diện ──────────────────────────────
    def _build_ui(self):
        pad = dict(padx=16, pady=8)

        # Tiêu đề
        tk.Label(
            self,
            text="Edit Template",
            bg=THEME["bg"],
            fg=THEME["accent2"],
            font=FONT_TITLE,
        ).pack(anchor="w", padx=16, pady=(14, 4))

        ttk.Separator(self).pack(fill="x", padx=16)

        # Chọn ngôn ngữ
        row_lang = tk.Frame(self, bg=THEME["bg"])
        row_lang.pack(fill="x", **pad)

        tk.Label(
            row_lang,
            text="Ngôn ngữ lập trình:",
            bg=THEME["bg"],
            fg=THEME["text"],
            font=FONT_LABEL,
            width=12,
            anchor="w",
        ).pack(side="left")

        self.lang_var = tk.StringVar(value=list(self.templates.keys())[0])

        combo = ttk.Combobox(
            row_lang,
            textvariable=self.lang_var,
            values=list(self.templates.keys()),
            state="readonly",
            style="Dark.TCombobox",
            width=14,
        )
        combo.pack(side="left", padx=(0, 8))
        combo.bind("<<ComboboxSelected>>", lambda _: self._load_language(self.lang_var.get()))

        # Extension (chỉ đọc)
        tk.Label(
            row_lang,
            text="Extension:",
            bg=THEME["bg"],
            fg=THEME["text_dim"],
            font=FONT_LABEL,
        ).pack(side="left", padx=(16, 4))

        self.ext_var = tk.StringVar()
        tk.Label(
            row_lang,
            textvariable=self.ext_var,
            bg=THEME["bg"],
            fg=THEME["accent2"],
            font=FONT_LABEL,
        ).pack(side="left")

        # Template format
        tk.Label(
            self,
            text="Template format  (dùng {problem} và {solution}):",
            bg=THEME["bg"],
            fg=THEME["text"],
            font=FONT_LABEL,
        ).pack(anchor="w", padx=16)

        text_frame, self.text_template = styled_text(self, height=14)
        text_frame.pack(fill="both", expand=True, padx=16, pady=4)

        # Nút Save
        btn_row = tk.Frame(self, bg=THEME["bg"])
        btn_row.pack(fill="x", padx=16, pady=(4, 14))

        styled_button(btn_row, "Save Template", self._save_template, accent=True, width=18).pack(side="right")
        styled_button(btn_row, "Close", self.destroy, accent=False, width=12).pack(side="right", padx=(0, 8))

        # Gợi ý
        tk.Label(
            self,
            text="Tip: {problem} -> đề bài   |   {solution} -> code",
            bg=THEME["bg"],
            fg=THEME["text_dim"],
            font=("Segoe UI", 8),
        ).pack(anchor="w", padx=16, pady=(0, 10))

    # ── load template theo ngôn ngữ ─────────────────────
    def _load_language(self, lang: str):
        tmpl = self.templates.get(lang, {})
        self.ext_var.set(tmpl.get("ext", ""))

        self.text_template.delete("1.0", "end")
        self.text_template.insert("1.0", tmpl.get("format", ""))

    # ── lưu template ────────────────────────────────────
    def _save_template(self):
        lang        = self.lang_var.get()
        new_format  = self.text_template.get("1.0", "end-1c")

        if "{problem}" not in new_format or "{solution}" not in new_format:
            messagebox.showwarning(
                "Thiếu placeholder",
                "Template phải chứa cả {problem} và {solution}.",
                parent=self,
            )
            return

        # Cập nhật dict gốc (runtime)
        self.templates[lang]["format"] = new_format
        messagebox.showinfo(
            "Đã lưu",
            f"Template cho {lang} đã được cập nhật!",
            parent=self,
        )


# ═══════════════════════════════════════════════════════
#  CỬA SỔ CHÍNH
# ═══════════════════════════════════════════════════════

class CodeTemplateApp(tk.Tk):
    """Cửa sổ chính của ứng dụng Code Template Generator."""

    def __init__(self):
        super().__init__()
        # Sao chép template để có thể chỉnh runtime
        self.templates = {
            lang: dict(data) for lang, data in DEFAULT_TEMPLATES.items()
        }

        self.title("Code Template Generator")
        self.configure(bg=THEME["bg"])
        self.geometry("800x700")
        self.minsize(640, 560)

        # Căn giữa màn hình
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"+{(sw-800)//2}+{(sh-700)//2}")

        self._apply_ttk_style()
        self._build_ui()

    # ── style toàn cục ──────────────────────────────
    def _apply_ttk_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        # Scrollbar
        style.configure(
            "Vertical.TScrollbar",
            background=THEME["bg_panel"],
            troughcolor=THEME["bg_input"],
            arrowcolor=THEME["text_dim"],
            bordercolor=THEME["bg_panel"],
            darkcolor=THEME["bg_panel"],
            lightcolor=THEME["bg_panel"],
        )
        style.map(
            "Vertical.TScrollbar",
            background=[("active", THEME["accent"])],
        )
        # Separator
        style.configure(
            "TSeparator",
            background=THEME["border"],
        )
        # Combobox
        style.configure(
            "Dark.TCombobox",
            fieldbackground=THEME["bg_input"],
            background=THEME["bg_input"],
            foreground=THEME["text"],
            arrowcolor=THEME["accent"],
            bordercolor=THEME["border"],
            selectbackground=THEME["accent"],
            selectforeground=THEME["btn_fg"],
        )

    # ── xây dựng giao diện chính ────────────────────────
    def _build_ui(self):
        # ── Header ──────────────────────────────────────
        header = tk.Frame(self, bg=THEME["accent"], height=52)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="</> Code Template Generator",
            bg=THEME["accent"],
            fg=THEME["btn_fg"],
            font=("Segoe UI", 13, "bold"),
        ).pack(side="left", padx=18, pady=0)

        tk.Label(
            header,
            text="Tạo file bài tập lập trình",
            bg=THEME["accent"],
            fg="#D5CCFF",
            font=("Segoe UI", 9),
        ).pack(side="left", padx=4)

        # ── Scrollable main area ─────────────────────────
        canvas = tk.Canvas(self, bg=THEME["bg"], highlightthickness=0)
        v_scroll = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=v_scroll.set)

        v_scroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self.main_frame = tk.Frame(canvas, bg=THEME["bg"])
        canvas_window = canvas.create_window((0, 0), window=self.main_frame, anchor="nw")

        def _on_frame_configure(_):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)

        self.main_frame.bind("<Configure>", _on_frame_configure)
        canvas.bind("<Configure>", _on_canvas_configure)

        # Mouse wheel scroll
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        self._build_form(self.main_frame)

    # ── form nhập liệu ──────────────────────────────────
    def _build_form(self, parent):
        p = dict(padx=20, pady=6)

        # ── Section: Thông tin file ──────────────────────
        self._section_title(parent, "Thêng tin file")

        row1 = tk.Frame(parent, bg=THEME["bg"])
        row1.pack(fill="x", **p)

        # Tên file
        col_name = tk.Frame(row1, bg=THEME["bg"])
        col_name.pack(side="left", fill="x", expand=True, padx=(0, 12))

        styled_label(col_name, "Tên file", bg=THEME["bg"]).pack(anchor="w", pady=(0, 3))
        self.entry_filename = styled_entry(col_name)
        self.entry_filename.pack(fill="x", ipady=5)

        # Ngôn ngữ
        col_lang = tk.Frame(row1, bg=THEME["bg"], width=160)
        col_lang.pack(side="right")
        col_lang.pack_propagate(False)

        styled_label(col_lang, "Ngôn ngữ lập trình", bg=THEME["bg"]).pack(anchor="w", pady=(0, 3))
        self.lang_var = tk.StringVar(value="Python")
        combo = ttk.Combobox(
            col_lang,
            textvariable=self.lang_var,
            values=list(self.templates.keys()),
            state="readonly",
            style="Dark.TCombobox",
            width=14,
        )
        combo.pack(fill="x", ipady=3)

        # Thư mục lưu
        row_dir = tk.Frame(parent, bg=THEME["bg"])
        row_dir.pack(fill="x", **p)

        styled_label(row_dir, "Thư mục lưu file", bg=THEME["bg"]).pack(anchor="w", pady=(0, 3))

        dir_row = tk.Frame(row_dir, bg=THEME["bg"])
        dir_row.pack(fill="x")

        self.save_dir_var = tk.StringVar(value=os.getcwd())
        entry_dir = styled_entry(dir_row, textvariable=self.save_dir_var)
        entry_dir.pack(side="left", fill="x", expand=True, ipady=5)

        browse_btn = tk.Button(
            dir_row,
            text="  Browse",
            command=self._browse_directory,
            bg=THEME["bg_panel"],
            fg=THEME["text"],
            font=FONT_BTN,
            relief="flat",
            cursor="hand2",
            padx=8,
            pady=5,
            activebackground=THEME["border"],
            activeforeground=THEME["text"],
            highlightthickness=1,
            highlightbackground=THEME["border"],
        )
        browse_btn.pack(side="left", padx=(6, 0))

        ttk.Separator(parent).pack(fill="x", padx=20, pady=8)

        # ── Section: Đề bài ─────────────────────────────
        self._section_title(parent, "Đề bài")

        problem_frame, self.text_problem = styled_text(parent, height=9)
        problem_frame.pack(fill="both", expand=True, padx=20, pady=(0, 6))

        ttk.Separator(parent).pack(fill="x", padx=20, pady=8)

        # ── Section: Lời giải ───────────────────────────
        self._section_title(parent, "Lời giải (Code)")

        solution_frame, self.text_solution = styled_text(parent, height=11)
        solution_frame.pack(fill="both", expand=True, padx=20, pady=(0, 6))

        ttk.Separator(parent).pack(fill="x", padx=20, pady=8)

        # ── Nút hành động ───────────────────────────────
        btn_row = tk.Frame(parent, bg=THEME["bg"])
        btn_row.pack(fill="x", padx=20, pady=(0, 20))

        styled_button(
            btn_row,
            "Create File",
            self._create_file,
            accent=True,
            width=18,
        ).pack(side="left")

        styled_button(
            btn_row,
            "Edit Template",
            self._open_edit_template,
            accent=False,
            width=18,
        ).pack(side="left", padx=(10, 0))

        styled_button(
            btn_row,
            "Clear All",
            self._clear_all,
            accent=False,
            width=12,
        ).pack(side="right")

        # ── Status bar ──────────────────────────────────
        self.status_var = tk.StringVar(value="Sẵn sàng.")
        status_bar = tk.Label(
            self,
            textvariable=self.status_var,
            bg=THEME["bg_panel"],
            fg=THEME["text_dim"],
            font=("Segoe UI", 8),
            anchor="w",
            padx=12,
            pady=4,
        )
        status_bar.pack(side="bottom", fill="x")

    # ── tiêu đề section ─────────────────────────────────
    def _section_title(self, parent, text: str):
        tk.Label(
            parent,
            text=text,
            bg=THEME["bg"],
            fg=THEME["accent2"],
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", padx=20, pady=(6, 2))

    # ─────────────────────────────────────────────
    #  XỬ LÝ SỰ KIỆN
    # ─────────────────────────────────────────────

    def _browse_directory(self):
        """Mở dialog chọn thư mục lưu file."""
        chosen = filedialog.askdirectory(
            title="Chọn thư mục lưu file",
            initialdir=self.save_dir_var.get(),
        )
        if chosen:
            self.save_dir_var.set(chosen)
            self._set_status(f"Thư mục: {chosen}")

    def _create_file(self):
        """Đọc dữ liệu -> validate -> tạo file."""
        file_name     = self.entry_filename.get().strip()
        language      = self.lang_var.get().strip()
        problem_text  = self.text_problem.get("1.0", "end-1c").strip()
        solution_text = self.text_solution.get("1.0", "end-1c").strip()
        save_dir      = self.save_dir_var.get().strip()

        # ── Kiểm tra đầu vào ────────────────────────────
        if not file_name:
            messagebox.showerror("Lỗi", "Vui lòng nhập tên file!")
            self.entry_filename.focus_set()
            return

        if not language or language not in self.templates:
            messagebox.showerror("Lỗi", "Vui lòng chọn ngôn ngữ lập trình!")
            return

        # ── Lấy template ────────────────────────────────
        tmpl    = self.templates[language]
        ext     = tmpl["ext"]
        fmt     = tmpl["format"]

        # ── Tạo nội dung file ───────────────────────────
        try:
            content = fmt.format(
                problem=problem_text  if problem_text  else "(Chưa có đề bài)",
                solution=solution_text if solution_text else "(Chưa có lời giải)",
            )
        except KeyError as exc:
            messagebox.showerror(
                "Lỗi Template",
                f"Template bị lỗi placeholder: {exc}\n"
                "Vào 'Edit Template' để kiểm tra lại.",
            )
            return

        # ── Đường dẫn đầy đủ ────────────────────────────
        full_filename = file_name + ext
        # Tránh ký tự không hợp lệ trong tên file
        illegal = r'\/:*?"<>|'
        for ch in illegal:
            if ch in full_filename:
                messagebox.showerror(
                    "Tên file không hợp lệ",
                    f"Tên file không được chứa kí tự: {illegal}",
                )
                return

        os.makedirs(save_dir, exist_ok=True)
        full_path = os.path.join(save_dir, full_filename)

        # ── Cảnh báo nếu file đã tồn tại ────────────────
        if os.path.exists(full_path):
            overwrite = messagebox.askyesno(
                "File đã tồn tại",
                f"'{full_filename}' đã tồn tại.\nBạn có muốn ghi đè không?",
            )
            if not overwrite:
                return

        # ── Ghi file ────────────────────────────────────
        try:
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
        except OSError as exc:
            messagebox.showerror("Lỗi ghi file", f"Không thể ghi file:\n{exc}")
            return

        # ── Thông báo thành công ─────────────────────────
        self._set_status(f"Da tao: {full_path}")
        messagebox.showinfo(
            "Tạo file thành công!",
            f"File đã tạo thành công:\n{full_path}",
        )

    def _open_edit_template(self):
        """Mở cửa sổ chỉnh sửa template."""
        win = EditTemplateWindow(self, self.templates)
        win.grab_set()   # modal
        self.wait_window(win)

    def _clear_all(self):
        """Xoá toàn bộ nội dung nhập liệu."""
        confirm = messagebox.askyesno("Xác nhận", "Xóa toàn bộ nội dung đã nhập?")
        if confirm:
            self.entry_filename.delete(0, "end")
            self.text_problem.delete("1.0", "end")
            self.text_solution.delete("1.0", "end")
            self.lang_var.set("Python")
            self._set_status("Đã xóa toàn bộ.")

    def _set_status(self, msg: str):
        """Cập nhật thanh trạng thái."""
        self.status_var.set(msg)
        self.update_idletasks()


# ═══════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    app = CodeTemplateApp()
    app.mainloop()
