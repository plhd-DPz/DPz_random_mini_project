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
            "/*==========================================================\n"
            "{problem}\n"
            "==========================================================*/\n\n"
            "{solution}"
        ),
    },
    "Python": {
        "ext": ".py",
        "format": (
            '"""\n'
            "============================================================\n"
            "{problem}\n"
            "============================================================\n"
            '"""\n\n'
            "{solution}"
        ),
    },
    "Java": {
        "ext": ".java",
        "format": (
            "/*==========================================================\n"
            "{problem}\n"
            "==========================================================*/\n\n"
            "{solution}"
        ),
    },
}

# ─────────────────────────────────────────────
#  BẢNG MÀU & FONT
# ─────────────────────────────────────────────
THEME = {
    "bg":           "#1E1E2E",
    "bg_panel":     "#252538",
    "bg_input":     "#2A2A3F",
    "accent":       "#7C6AF7",
    "accent2":      "#5EEAD4",
    "accent_hover": "#9580FF",
    "text":         "#CDD6F4",
    "text_dim":     "#6C7086",
    "border":       "#383851",
    "btn_fg":       "#FFFFFF",
}

FONT_MAIN  = ("Consolas", 10)
FONT_LABEL = ("Segoe UI", 9, "bold")
FONT_TITLE = ("Segoe UI", 13, "bold")
FONT_MONO  = ("Consolas", 10)
FONT_BTN   = ("Segoe UI", 9, "bold")


# ═══════════════════════════════════════════════════════
#  WIDGET TIỆN ÍCH
# ═══════════════════════════════════════════════════════

def styled_label(parent, text, **kw):
    """Label với style mặc định."""
    cfg = dict(
        text=text, bg=THEME["bg"], fg=THEME["text"],
        font=FONT_LABEL, anchor="w",
    )
    cfg.update(kw)
    return tk.Label(parent, **cfg)


def styled_entry(parent, **kw):
    """Entry với style dark theme."""
    cfg = dict(
        bg=THEME["bg_input"], fg=THEME["text"],
        insertbackground=THEME["accent2"],
        relief="flat", font=FONT_MAIN,
        highlightthickness=1,
        highlightbackground=THEME["border"],
        highlightcolor=THEME["accent"],
    )
    cfg.update(kw)
    return tk.Entry(parent, **cfg)


def styled_text(parent, height=10, **kw):
    """
    Text widget có scrollbar dọc, dark theme.

    Lưu ý khi pack frame trả về trong canvas scroll area:
      - Dùng fill="x"  (KHÔNG expand=True)
      - Chiều cao được kiểm soát hoàn toàn bởi tham số `height` (số dòng)
      - Tránh reflow thay đổi kích thước khi canvas cập nhật scrollregion
    """
    frame = tk.Frame(parent, bg=THEME["border"], padx=1, pady=1)

    cfg = dict(
        bg=THEME["bg_input"], fg=THEME["text"],
        insertbackground=THEME["accent2"],
        relief="flat", font=FONT_MONO,
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


def styled_button(parent, text, command, accent=True, width=18, **kw):
    """Button với hiệu ứng hover."""
    bg_normal = THEME["accent"]       if accent else THEME["bg_panel"]
    bg_hover  = THEME["accent_hover"] if accent else THEME["border"]
    fg        = THEME["btn_fg"]

    btn = tk.Button(
        parent, text=text, command=command,
        bg=bg_normal, fg=fg, font=FONT_BTN,
        relief="flat", cursor="hand2",
        width=width, padx=10, pady=6,
        activebackground=bg_hover, activeforeground=fg,
        borderwidth=0, **kw,
    )
    btn.bind("<Enter>", lambda _: btn.config(bg=bg_hover))
    btn.bind("<Leave>", lambda _: btn.config(bg=bg_normal))
    return btn


# ═══════════════════════════════════════════════════════
#  CỬA SỔ CHỈNH SỬA TEMPLATE
# ═══════════════════════════════════════════════════════

class EditTemplateWindow(tk.Toplevel):
    """Cửa sổ con cho phép xem & chỉnh sửa template theo từng ngôn ngữ."""

    def __init__(self, parent, templates: dict, on_saved=None):
        super().__init__(parent)
        self.templates = templates   # tham chiếu dict gốc
        self.on_saved  = on_saved    # callback() sau khi lưu thành công

        self.title("Edit Templates")
        self.configure(bg=THEME["bg"])
        self.resizable(True, True)
        self.geometry("660x560")
        self.minsize(520, 440)

        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width()  - 660) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 560) // 2
        self.geometry(f"+{x}+{y}")

        self._build_ui()
        self._load_language(self.lang_var.get())

    def _build_ui(self):
        PAD = dict(padx=16, pady=6)

        # Tiêu đề
        tk.Label(
            self, text="Edit Template",
            bg=THEME["bg"], fg=THEME["accent2"],
            font=FONT_TITLE,
        ).pack(anchor="w", padx=16, pady=(14, 4))

        ttk.Separator(self).pack(fill="x", padx=16, pady=(0, 8))

        # ── Hàng chọn ngôn ngữ + extension ─────────────
        row_lang = tk.Frame(self, bg=THEME["bg"])
        row_lang.pack(fill="x", **PAD)

        tk.Label(
            row_lang, text="Ngôn ngữ:",
            bg=THEME["bg"], fg=THEME["text_dim"],
            font=FONT_LABEL,
        ).pack(side="left", padx=(0, 8))

        self.lang_var = tk.StringVar(value=list(self.templates.keys())[0])

        self.lang_combo = ttk.Combobox(
            row_lang,
            textvariable=self.lang_var,
            values=list(self.templates.keys()),
            state="readonly",
            style="Dark.TCombobox",
            width=14,
            font=FONT_MAIN,
        )
        self.lang_combo.pack(side="left")
        self.lang_combo.bind("<<ComboboxSelected>>",
                             lambda _: self._load_language(self.lang_var.get()))

        tk.Label(
            row_lang, text="Extension:",
            bg=THEME["bg"], fg=THEME["text_dim"],
            font=FONT_LABEL,
        ).pack(side="left", padx=(20, 6))

        self.ext_var = tk.StringVar()
        styled_entry(row_lang, textvariable=self.ext_var, width=8).pack(
            side="left", ipady=3)

        # ── Label hướng dẫn ─────────────────────────────
        tk.Label(
            self,
            text="Template format  (dùng {problem} và {solution}):",
            bg=THEME["bg"], fg=THEME["text"],
            font=FONT_LABEL,
        ).pack(anchor="w", padx=16)

        # ── Text editor (expand=True ổn vì đây là Toplevel riêng) ──
        editor_container = tk.Frame(self, bg=THEME["bg"])
        editor_container.pack(fill="both", expand=True, padx=16, pady=6)

        text_frame, self.text_template = styled_text(editor_container, height=16)
        text_frame.pack(fill="both", expand=True)

        tk.Label(
            self,
            text="  Tip: {problem} → đề bài   |   {solution} → code",
            bg=THEME["bg"], fg=THEME["text_dim"],
            font=("Segoe UI", 8),
        ).pack(anchor="w", padx=16)

        ttk.Separator(self).pack(fill="x", padx=16, pady=(6, 0))

        btn_row = tk.Frame(self, bg=THEME["bg"])
        btn_row.pack(fill="x", padx=16, pady=(8, 14))

        styled_button(btn_row, "Save Template", self._save_template,
                      accent=True, width=18).pack(side="right")
        styled_button(btn_row, "✖  Close", self.destroy,
                      accent=False, width=10).pack(side="right", padx=(0, 8))

    def _load_language(self, lang: str):
        tmpl = self.templates.get(lang, {})
        self.ext_var.set(tmpl.get("ext", ""))
        self.text_template.delete("1.0", "end")
        self.text_template.insert("1.0", tmpl.get("format", ""))

    def _save_template(self):
        lang       = self.lang_var.get()
        new_format = self.text_template.get("1.0", "end-1c")
        new_ext    = self.ext_var.get().strip()

        if "{problem}" not in new_format or "{solution}" not in new_format:
            messagebox.showwarning(
                "Thiếu placeholder",
                "Template phải chứa cả {problem} và {solution}.",
                parent=self,
            )
            return

        if not new_ext:
            messagebox.showwarning(
                "Thiếu extension",
                "Vui lòng nhập extension (ví dụ: .c, .py).",
                parent=self,
            )
            return

        if not new_ext.startswith("."):
            new_ext = "." + new_ext

        self.templates[lang]["format"] = new_format
        self.templates[lang]["ext"]    = new_ext

        if self.on_saved:
            self.on_saved()

        messagebox.showinfo(
            "Đã lưu",
            f"Template cho '{lang}' đã được cập nhật!\nExtension: {new_ext}",
            parent=self,
        )


# ═══════════════════════════════════════════════════════
#  CỬA SỔ CHÍNH
# ═══════════════════════════════════════════════════════

class CodeTemplateApp(tk.Tk):
    """Cửa sổ chính của ứng dụng Code Template Generator."""

    def __init__(self):
        super().__init__()
        self.templates = {lang: dict(data) for lang, data in DEFAULT_TEMPLATES.items()}

        self.title("Code Template Generator")
        self.configure(bg=THEME["bg"])
        self.geometry("800x700")
        self.minsize(640, 560)

        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"+{(sw - 800)//2}+{(sh - 700)//2}")

        self._apply_ttk_style()
        self._build_ui()

    # ── TTK style ───────────────────────────────────────
    def _apply_ttk_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure(
            "Vertical.TScrollbar",
            background=THEME["bg_panel"],
            troughcolor=THEME["bg_input"],
            arrowcolor=THEME["text_dim"],
            bordercolor=THEME["bg_panel"],
            darkcolor=THEME["bg_panel"],
            lightcolor=THEME["bg_panel"],
        )
        style.map("Vertical.TScrollbar",
                  background=[("active", THEME["accent"])])

        style.configure("TSeparator", background=THEME["border"])

        style.configure(
            "Dark.TCombobox",
            fieldbackground=THEME["bg_input"],
            background=THEME["bg_input"],
            foreground=THEME["text"],
            arrowcolor=THEME["accent"],
            bordercolor=THEME["border"],
            selectbackground=THEME["accent"],
            selectforeground=THEME["btn_fg"],
            insertcolor=THEME["text"],
            padding=(6, 4),
        )
        style.map(
            "Dark.TCombobox",
            fieldbackground=[("readonly", THEME["bg_input"]),
                             ("disabled", THEME["bg_panel"])],
            foreground=[("readonly", THEME["text"]),
                        ("disabled", THEME["text_dim"])],
            background=[("readonly", THEME["bg_input"]),
                        ("active",   THEME["bg_panel"])],
            arrowcolor=[("readonly", THEME["accent"])],
        )

    # ── UI chính ────────────────────────────────────────
    def _build_ui(self):
        # Header
        header = tk.Frame(self, bg=THEME["accent"], height=52)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header, text="</> Code Template Generator",
            bg=THEME["accent"], fg=THEME["btn_fg"],
            font=("Segoe UI", 13, "bold"),
        ).pack(side="left", padx=18)

        tk.Label(
            header, text="Tạo file bài tập lập trình theo template",
            bg=THEME["accent"], fg="#D5CCFF",
            font=("Segoe UI", 9),
        ).pack(side="left", padx=4)

        # Scrollable canvas area
        canvas   = tk.Canvas(self, bg=THEME["bg"], highlightthickness=0)
        v_scroll = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=v_scroll.set)

        v_scroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self.main_frame = tk.Frame(canvas, bg=THEME["bg"])
        canvas_window   = canvas.create_window(
            (0, 0), window=self.main_frame, anchor="nw")

        self.main_frame.bind(
            "<Configure>",
            lambda _: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfig(canvas_window, width=e.width),
        )
        canvas.bind_all(
            "<MouseWheel>",
            lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"),
        )

        self._build_form(self.main_frame)

    # ── Form ────────────────────────────────────────────
    def _build_form(self, parent):
        P = dict(padx=20, pady=6)

        # ══ Section: Thông tin file ═════════════════════
        self._section_title(parent, "Thông tin file")

        # Hàng: Tên file (trái, co giãn) | Ngôn ngữ (phải, cố định)
        row_top = tk.Frame(parent, bg=THEME["bg"])
        row_top.pack(fill="x", **P)

        col_name = tk.Frame(row_top, bg=THEME["bg"])
        col_name.pack(side="left", fill="x", expand=True, padx=(0, 16))

        styled_label(col_name, "Tên file").pack(anchor="w", pady=(0, 3))
        self.entry_filename = styled_entry(col_name)
        self.entry_filename.pack(fill="x", ipady=5)

        col_lang = tk.Frame(row_top, bg=THEME["bg"])
        col_lang.pack(side="right")

        styled_label(col_lang, "Ngôn ngữ").pack(anchor="w", pady=(0, 3))

        self.lang_var = tk.StringVar(value="C")

        lang_row = tk.Frame(col_lang, bg=THEME["bg"])
        lang_row.pack(anchor="w")

        self.lang_combo = ttk.Combobox(
            lang_row,
            textvariable=self.lang_var,
            values=list(self.templates.keys()),
            state="readonly",
            style="Dark.TCombobox",
            width=12,
            font=FONT_MAIN,
        )
        self.lang_combo.pack(side="left")

        # Label extension nhỏ bên phải combobox
        self.ext_label_var = tk.StringVar()
        tk.Label(
            lang_row,
            textvariable=self.ext_label_var,
            bg=THEME["bg"], fg=THEME["accent2"],
            font=("Consolas", 9, "bold"),
        ).pack(side="left", padx=(8, 0))

        # Cập nhật ext label mỗi khi đổi ngôn ngữ
        self.lang_var.trace_add("write", self._on_language_change)

        # Thư mục lưu
        row_dir = tk.Frame(parent, bg=THEME["bg"])
        row_dir.pack(fill="x", **P)

        styled_label(row_dir, "Thư mục lưu file").pack(anchor="w", pady=(0, 3))

        dir_row = tk.Frame(row_dir, bg=THEME["bg"])
        dir_row.pack(fill="x")

        self.save_dir_var = tk.StringVar(value=os.getcwd())
        styled_entry(dir_row, textvariable=self.save_dir_var).pack(
            side="left", fill="x", expand=True, ipady=5)

        tk.Button(
            dir_row, text="  Browse",
            command=self._browse_directory,
            bg=THEME["bg_panel"], fg=THEME["text"],
            font=FONT_BTN, relief="flat", cursor="hand2",
            padx=8, pady=5,
            activebackground=THEME["border"],
            activeforeground=THEME["text"],
            highlightthickness=1,
            highlightbackground=THEME["border"],
        ).pack(side="left", padx=(6, 0))

        ttk.Separator(parent).pack(fill="x", padx=20, pady=8)

        # ══ Section: Đề bài ═════════════════════════════
        self._section_title(parent, "Đề bài")

        problem_frame, self.text_problem = styled_text(parent, height=9)
        # fill="x" (không expand=True) → chiều cao cố định theo `height`,
        # không bị reflow khi canvas thay đổi width hoặc scrollregion
        problem_frame.pack(fill="x", padx=20, pady=(0, 6))

        ttk.Separator(parent).pack(fill="x", padx=20, pady=8)

        # ══ Section: Lời giải ═══════════════════════════
        self._section_title(parent, "Lời giải (Code)")

        solution_frame, self.text_solution = styled_text(parent, height=14)
        solution_frame.pack(fill="x", padx=20, pady=(0, 6))  # fill="x", không expand

        ttk.Separator(parent).pack(fill="x", padx=20, pady=8)

        # ── Nút hành động ───────────────────────────────
        btn_row = tk.Frame(parent, bg=THEME["bg"])
        btn_row.pack(fill="x", padx=20, pady=(0, 20))

        styled_button(btn_row, "Create File",   self._create_file,
                      accent=True,  width=16).pack(side="left")
        styled_button(btn_row, "Edit Template", self._open_edit_template,
                      accent=False, width=16).pack(side="left", padx=(10, 0))
        styled_button(btn_row, "Clear All",     self._clear_all,
                      accent=False, width=12).pack(side="right")

        # Status bar
        self.status_var = tk.StringVar(value="Sẵn sàng.")
        tk.Label(
            self,
            textvariable=self.status_var,
            bg=THEME["bg_panel"], fg=THEME["text_dim"],
            font=("Segoe UI", 8),
            anchor="w", padx=12, pady=4,
        ).pack(side="bottom", fill="x")

        self._on_language_change()   # khởi tạo ban đầu

    def _section_title(self, parent, text: str):
        tk.Label(
            parent, text=text,
            bg=THEME["bg"], fg=THEME["accent2"],
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", padx=20, pady=(6, 2))

    # ── Sự kiện ─────────────────────────────────────────

    def _on_language_change(self, *_):
        """Cập nhật label extension khi đổi ngôn ngữ."""
        lang = self.lang_var.get()
        ext  = self.templates.get(lang, {}).get("ext", "")
        self.ext_label_var.set(f"→  {ext}" if ext else "")
        self._set_status(f"Ngôn ngữ: {lang}  ({ext})")

    def _browse_directory(self):
        chosen = filedialog.askdirectory(
            title="Chọn thư mục lưu file",
            initialdir=self.save_dir_var.get(),
        )
        if chosen:
            self.save_dir_var.set(chosen)
            self._set_status(f"Thư mục: {chosen}")

    def _create_file(self):
        """Đọc dữ liệu → validate → render template → ghi file."""
        file_name     = self.entry_filename.get().strip()
        language      = self.lang_var.get().strip()
        problem_text  = self.text_problem.get("1.0",  "end-1c").strip()
        solution_text = self.text_solution.get("1.0", "end-1c").strip()
        save_dir      = self.save_dir_var.get().strip()

        if not file_name:
            messagebox.showerror("Lỗi", "Vui lòng nhập tên file!")
            self.entry_filename.focus_set()
            return

        if not language or language not in self.templates:
            messagebox.showerror("Lỗi", "Vui lòng chọn ngôn ngữ lập trình!")
            return

        tmpl = self.templates[language]
        ext  = tmpl["ext"]
        fmt  = tmpl["format"]

        try:
            content = fmt.format(
                problem  = problem_text  or "(Chưa có đề bài)",
                solution = solution_text or "(Chưa có lời giải)",
                filename = file_name,
            )
        except KeyError as exc:
            messagebox.showerror(
                "Lỗi Template",
                f"Template bị lỗi placeholder: {exc}\n"
                "Vào 'Edit Template' để kiểm tra lại.",
            )
            return

        full_filename = file_name + ext
        illegal = r'\/:*?"<>|'
        if any(ch in full_filename for ch in illegal):
            messagebox.showerror(
                "Tên file không hợp lệ",
                f"Tên file không được chứa các ký tự: {illegal}",
            )
            return

        os.makedirs(save_dir, exist_ok=True)
        full_path = os.path.join(save_dir, full_filename)

        if os.path.exists(full_path):
            if not messagebox.askyesno(
                "File đã tồn tại",
                f"'{full_filename}' đã tồn tại.\nBạn có muốn ghi đè không?",
            ):
                return

        try:
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
        except OSError as exc:
            messagebox.showerror("Lỗi ghi file", f"Không thể ghi file:\n{exc}")
            return

        self._set_status(f"Đã tạo: {full_path}")
        messagebox.showinfo("Tạo file thành công!", f"File đã tạo:\n{full_path}")

    def _open_edit_template(self):
        """Mở cửa sổ chỉnh sửa template (modal)."""
        def _on_saved():
            # Đồng bộ danh sách ngôn ngữ trong combobox sau khi lưu
            self.lang_combo.configure(values=list(self.templates.keys()))
            self._on_language_change()

        win = EditTemplateWindow(self, self.templates, on_saved=_on_saved)
        win.grab_set()
        self.wait_window(win)

    def _clear_all(self):
        if messagebox.askyesno("Xác nhận", "Xóa toàn bộ nội dung đã nhập?"):
            self.entry_filename.delete(0, "end")
            self.text_problem.delete("1.0", "end")
            self.text_solution.delete("1.0", "end")
            self.lang_var.set("C")
            self._set_status("Đã xóa toàn bộ.")

    def _set_status(self, msg: str):
        self.status_var.set(msg)
        self.update_idletasks()


# ═══════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    app = CodeTemplateApp()
    app.mainloop()
