"""
Time Manager Desktop App v2
Weekly planner with one-time and repeating notes, yearly calendar, and floating action button.
Data format: DATE|HH:MM-HH:MM|Heading|Content|type
  DATE = YYYY-MM-DD (one-time) or W{n} where n=1-7 Mon-Sun (weekly)
  type = once | weekly
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import datetime
import calendar as cal_module

# ════════════════════════════════════════════════════════════════
# CONSTANTS & COLORS
# ════════════════════════════════════════════════════════════════
C_BG         = "#F4F6F9"
C_SECONDARY  = "#E2E8F0"
C_ACCENT     = "#3B82F6"
C_ACCENT_LT  = "#DBEAFE"
C_ACCENT_DK  = "#1D4ED8"
C_WHITE      = "#FFFFFF"
C_TEXT       = "#1E293B"
C_SUBTEXT    = "#64748B"
C_BORDER     = "#CBD5E1"

# One-time note  -> orange
C_ONCE_BG    = "#FFF7ED"
C_ONCE_BD    = "#FDBA74"
C_ONCE_FG    = "#C2410C"

# Weekly note    -> blue
C_WKLY_BG    = "#EFF6FF"
C_WKLY_BD    = "#93C5FD"
C_WKLY_FG    = "#1D4ED8"

C_REST       = "#F8FAFC"
C_TODAY_HDR  = "#1D4ED8"
C_TODAY_FG   = "#FFFFFF"
C_OTHER_HDR  = "#DBEAFE"
C_OTHER_FG   = "#1E293B"

DATA_FILE    = "data.txt"

WDAY_NAMES   = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
WDAY_SHORT   = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]

# ════════════════════════════════════════════════════════════════
# DATA LAYER
# ════════════════════════════════════════════════════════════════

def load_tasks():
    """Load all tasks from data.txt. Returns list of dicts."""
    tasks = []
    if not os.path.exists(DATA_FILE):
        open(DATA_FILE, "w", encoding="utf-8").close()
        return tasks
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split("|", 4)
            if len(parts) < 4:
                continue
            date_str   = parts[0]
            time_range = parts[1]
            heading    = parts[2]
            content    = parts[3]
            task_type  = parts[4] if len(parts) > 4 else "once"
            try:
                start_str, end_str = time_range.split("-")
                tasks.append({
                    "date":    date_str,
                    "start":   start_str,
                    "end":     end_str,
                    "heading": heading,
                    "content": content,
                    "type":    task_type,
                })
            except Exception:
                pass
    return tasks


def save_tasks(tasks):
    """Persist all tasks to data.txt."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        for t in tasks:
            line = (f"{t['date']}|{t['start']}-{t['end']}|"
                    f"{t['heading']}|{t['content']}|{t.get('type','once')}\n")
            f.write(line)


def time_to_min(t_str):
    """'HH:MM' → total minutes."""
    h, m = map(int, t_str.split(":"))
    return h * 60 + m


def times_overlap(sa, ea, sb, eb):
    """True if [sa,ea) overlaps [sb,eb)."""
    return time_to_min(sa) < time_to_min(eb) and time_to_min(sb) < time_to_min(ea)


def get_week_dates():
    """Return ISO strings for Mon-Sun of current week."""
    today   = datetime.date.today()
    monday  = today - datetime.timedelta(days=today.weekday())
    return [(monday + datetime.timedelta(days=i)).isoformat() for i in range(7)]


def resolve_tasks_for_week(tasks, week_dates):
    """
    Map each task to its resolved date within the given week.
    weekly tasks (W{n}) → date of that weekday in the week.
    once tasks          → their literal date (only if in the week).
    Returns list of (task, resolved_date_str).
    """
    week_set = set(week_dates)
    result   = []
    for t in tasks:
        if t.get("type") == "weekly":
            try:
                wday = int(t["date"][1:])            # 1=Mon … 7=Sun
                resolved = week_dates[wday - 1]
                result.append((t, resolved))
            except (ValueError, IndexError):
                pass
        else:
            if t["date"] in week_set:
                result.append((t, t["date"]))
    return result


def tasks_for_date(all_tasks, date_str):
    """Return tasks that should appear on date_str (once or weekly match)."""
    week_dates = get_week_dates()
    resolved   = resolve_tasks_for_week(all_tasks, week_dates)
    return sorted(
        [t for (t, d) in resolved if d == date_str],
        key=lambda x: time_to_min(x["start"])
    )


def date_has_any_task(all_tasks, d: datetime.date):
    """Quick check used by the year-calendar view."""
    d_str  = d.isoformat()
    d_wday = d.isoweekday()    # 1=Mon
    for t in all_tasks:
        if t.get("type") == "weekly":
            try:
                if int(t["date"][1:]) == d_wday:
                    return True
            except (ValueError, AttributeError):
                pass
        else:
            if t["date"] == d_str:
                return True
    return False


def check_conflict(tasks, date_key, start, end, task_type, exclude_idx=None):
    """
    Return the first conflicting task, or None.
    date_key: YYYY-MM-DD (once) or W{n} (weekly)
    """
    # Derive weekday for the new task
    if task_type == "weekly":
        new_wday = int(date_key[1:])
    else:
        new_wday = datetime.date.fromisoformat(date_key).isoweekday()

    for i, t in enumerate(tasks):
        if i == exclude_idx:
            continue
        if not times_overlap(start, end, t["start"], t["end"]):
            continue

        # Determine weekday of existing task
        if t.get("type") == "weekly":
            try:
                t_wday = int(t["date"][1:])
            except ValueError:
                continue
        else:
            try:
                t_wday = datetime.date.fromisoformat(t["date"]).isoweekday()
            except ValueError:
                continue

        # Conflict if same weekday (covers both once↔once and once↔weekly)
        if task_type == "once" and t.get("type") == "once":
            # strict: must be same calendar date
            if t["date"] != date_key:
                continue
        else:
            if t_wday != new_wday:
                continue

        return t
    return None


def get_next_task(tasks):
    """Return the first upcoming/ongoing task in the current week, or None."""
    week_dates = get_week_dates()
    resolved   = resolve_tasks_for_week(tasks, week_dates)
    now        = datetime.datetime.now()
    now_date   = now.date().isoformat()
    now_mins   = now.hour * 60 + now.minute
    candidates = []
    for (t, d) in resolved:
        if d < now_date:
            continue
        if d == now_date and time_to_min(t["end"]) <= now_mins:
            continue
        candidates.append((d, time_to_min(t["start"]), t))
    if not candidates:
        return None
    candidates.sort()
    return candidates[0][2]


def truncate(text, n):
    return text if len(text) <= n else text[:n - 3] + "..."


# ════════════════════════════════════════════════════════════════
# TIME-ENTRY WIDGET  
# ════════════════════════════════════════════════════════════════

class TimeEntry(tk.Entry):
    """
    auto-formats input to HH:MM.
    Typing "1650" becomes "16:50" automatically.
    Backspace is allowed without re-inserting characters.
    """

    def __init__(self, parent, **kwargs):
        self._var       = tk.StringVar()
        self._updating  = False
        self._prev_len  = 0
        super().__init__(parent, textvariable=self._var, **kwargs)
        self._var.trace_add("write", self._on_change)

    def _on_change(self, *_args):
        if self._updating:
            return
        val      = self._var.get()
        cur_len  = len(val)

        # Allow deletions without interference
        if cur_len < self._prev_len:
            self._prev_len = cur_len
            return

        self._updating = True
        digits = "".join(c for c in val if c.isdigit())
        if len(digits) > 4:
            digits = digits[:4]

        if len(digits) >= 3:
            formatted = digits[:2] + ":" + digits[2:4]
        elif len(digits) == 2:
            formatted = digits + ":"
        else:
            formatted = digits

        if formatted != val:
            self._var.set(formatted)
            self.icursor(len(formatted))

        self._prev_len = len(self._var.get())
        self._updating = False

    def get_time(self):
        return self._var.get()

    def set_time(self, val):
        self._var.set(val)
        self._prev_len = len(val)


# ════════════════════════════════════════════════════════════════
# UI HELPERS
# ════════════════════════════════════════════════════════════════

def styled_button(parent, text, command,
                  bg=C_ACCENT_LT, fg=C_ACCENT_DK,
                  font=None, padx=16, pady=8,
                  hover_bg=None, hover_fg=None):
    """Rounded-looking button (Frame+Label)."""
    if font is None:
        font = ("Segoe UI", 10, "bold")
    if hover_bg is None:
        hover_bg = C_ACCENT
    if hover_fg is None:
        hover_fg = C_WHITE

    frame = tk.Frame(parent, bg=bg, cursor="hand2",
                     highlightbackground=bg, highlightthickness=2)
    lbl   = tk.Label(frame, text=text, bg=bg, fg=fg,
                     font=font, padx=padx, pady=pady)
    lbl.pack()

    def on_click(_e):
        command()

    def on_enter(_e):
        frame.config(bg=hover_bg, highlightbackground=hover_bg)
        lbl.config(bg=hover_bg, fg=hover_fg)

    def on_leave(_e):
        frame.config(bg=bg, highlightbackground=bg)
        lbl.config(bg=bg, fg=fg)

    for w in (frame, lbl):
        w.bind("<Button-1>", on_click)
        w.bind("<Enter>",    on_enter)
        w.bind("<Leave>",    on_leave)

    return frame


def add_placeholder(entry: tk.Entry, var: tk.StringVar, placeholder: str):
    """Grey placeholder text for Entry widgets."""
    if not var.get():
        entry.insert(0, placeholder)
        entry.config(fg=C_SUBTEXT)

    def on_focus_in(_e):
        if entry.get() == placeholder:
            entry.delete(0, "end")
            entry.config(fg=C_TEXT)

    def on_focus_out(_e):
        if not entry.get():
            entry.insert(0, placeholder)
            entry.config(fg=C_SUBTEXT)

    entry.bind("<FocusIn>",  on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)


def add_text_placeholder(text_widget: tk.Text, placeholder: str):
    """Grey placeholder text for Text widgets."""
    text_widget.insert("1.0", placeholder)
    text_widget.config(fg=C_SUBTEXT)

    def on_focus_in(_e):
        if text_widget.get("1.0", "end-1c") == placeholder:
            text_widget.delete("1.0", "end")
            text_widget.config(fg=C_TEXT)

    def on_focus_out(_e):
        if not text_widget.get("1.0", "end-1c").strip():
            text_widget.insert("1.0", placeholder)
            text_widget.config(fg=C_SUBTEXT)

    text_widget.bind("<FocusIn>",  on_focus_in)
    text_widget.bind("<FocusOut>", on_focus_out)


def styled_entry(parent, textvariable=None, width=None, **kwargs):
    """Uniform rounded-ish entry field."""
    opts = dict(
        font=("Segoe UI", 10),
        bg=C_BG,
        relief="flat",
        highlightbackground=C_BORDER,
        highlightthickness=1,
    )
    opts.update(kwargs)
    if textvariable is not None:
        opts["textvariable"] = textvariable
    if width is not None:
        opts["width"] = width
    return tk.Entry(parent, **opts)


# ════════════════════════════════════════════════════════════════
# NOTE FORM WINDOW  (Add / Edit)
# ════════════════════════════════════════════════════════════════

class NoteFormWindow:
    """Toplevel for creating or editing a task."""

    def __init__(self, parent_app, task=None, task_idx=None):
        self.app         = parent_app
        self.editing_idx = task_idx

        self.win = tk.Toplevel(parent_app.root)
        self.win.title("Edit Task" if task else "Add Task")
        self.win.configure(bg=C_WHITE)
        self.win.resizable(False, False)
        self.win.transient(parent_app.root)   # associated but not modal – allows alt-tab

        self.win.geometry("460x450")
        self.win.update_idletasks()
        rx = parent_app.root.winfo_x()
        ry = parent_app.root.winfo_y()
        rw = parent_app.root.winfo_width()
        rh = parent_app.root.winfo_height()
        self.win.geometry(f"460x450+{rx + (rw-460)//2}+{ry + (rh-450)//2}")

        self._build(task)

    # ── Build UI ──────────────────────────────────────────────

    def _build(self, task):
        win = self.win
        PAD = 24

        # Title bar
        tk.Label(win, text="Edit Task" if task else "New Task",
                 bg=C_WHITE, fg=C_TEXT,
                 font=("Segoe UI", 14, "bold")
                 ).pack(anchor="w", padx=PAD, pady=(20, 4))
        tk.Frame(win, bg=C_BORDER, height=1).pack(fill="x", padx=PAD)

        body = tk.Frame(win, bg=C_WHITE)
        body.pack(fill="both", expand=True, padx=PAD, pady=12)

        # ── Task type ──
        type_row = tk.Frame(body, bg=C_WHITE)
        type_row.pack(fill="x", pady=(0, 12))
        tk.Label(type_row, text="Type:", bg=C_WHITE, fg=C_TEXT,
                 font=("Segoe UI", 10, "bold"), width=9, anchor="w").pack(side="left")

        self.type_var = tk.StringVar(value=task.get("type", "once") if task else "once")

        for val, label in (("once", "📅 One-time"), ("weekly", "🔁 Weekly")):
            tk.Radiobutton(
                type_row, text=label, variable=self.type_var, value=val,
                bg=C_WHITE, fg=C_TEXT, font=("Segoe UI", 10),
                activebackground=C_WHITE, selectcolor=C_WHITE,
                command=self._on_type_change
            ).pack(side="left", padx=(0, 20))

        # ── Date / Weekday ──
        self.date_container = tk.Frame(body, bg=C_WHITE)
        self.date_container.pack(fill="x", pady=(0, 10))

        # One-time: date entry
        self.date_row = tk.Frame(self.date_container, bg=C_WHITE)
        tk.Label(self.date_row, text="Date:", bg=C_WHITE, fg=C_TEXT,
                 font=("Segoe UI", 10, "bold"), width=9, anchor="w").pack(side="left")
        init_date = task["date"] if (task and task.get("type") != "weekly") else datetime.date.today().isoformat()
        self.date_var = tk.StringVar(value=init_date)
        date_entry = styled_entry(self.date_row, textvariable=self.date_var, width=14)
        date_entry.pack(side="left")
        tk.Label(self.date_row, text="(YYYY-MM-DD)", bg=C_WHITE, fg=C_SUBTEXT,
                 font=("Segoe UI", 9)).pack(side="left", padx=6)

        # Auto-pad date parts on focus-out
        date_entry.bind("<FocusOut>", self._autopad_date)

        # Weekly: weekday combobox
        self.wday_row = tk.Frame(self.date_container, bg=C_WHITE)
        tk.Label(self.wday_row, text="Day:", bg=C_WHITE, fg=C_TEXT,
                 font=("Segoe UI", 10, "bold"), width=9, anchor="w").pack(side="left")
        init_wday = "Monday"
        if task and task.get("type") == "weekly":
            try:
                init_wday = WDAY_NAMES[int(task["date"][1:]) - 1]
            except (ValueError, IndexError):
                pass
        self.wday_var = tk.StringVar(value=init_wday)
        ttk.Combobox(
            self.wday_row, textvariable=self.wday_var,
            values=WDAY_NAMES, state="readonly", width=14,
            font=("Segoe UI", 10)
        ).pack(side="left")

        # ── Time ──
        time_row = tk.Frame(body, bg=C_WHITE)
        time_row.pack(fill="x", pady=(0, 10))
        tk.Label(time_row, text="Time:", bg=C_WHITE, fg=C_TEXT,
                 font=("Segoe UI", 10, "bold"), width=9, anchor="w").pack(side="left")

        self.from_entry = TimeEntry(
            time_row, font=("Segoe UI Mono", 11), bg=C_BG, relief="flat",
            highlightbackground=C_BORDER, highlightthickness=1,
            width=7, justify="center")
        self.from_entry.set_time(task["start"] if task else "")
        self.from_entry.pack(side="left")

        tk.Label(time_row, text=" – ", bg=C_WHITE, fg=C_TEXT,
                 font=("Segoe UI", 11)).pack(side="left")

        self.to_entry = TimeEntry(
            time_row, font=("Segoe UI Mono", 11), bg=C_BG, relief="flat",
            highlightbackground=C_BORDER, highlightthickness=1,
            width=7, justify="center")
        self.to_entry.set_time(task["end"] if task else "")
        self.to_entry.pack(side="left")

        tk.Label(time_row, text=" (HH:MM)", bg=C_WHITE, fg=C_SUBTEXT,
                 font=("Segoe UI", 9)).pack(side="left")

        # Auto-advance focus after time entry is complete
        self.from_entry._var.trace_add("write", lambda *_: self._advance_if_done(self.from_entry, self.to_entry))
        self.to_entry._var.trace_add("write",   lambda *_: self._advance_if_done(self.to_entry,   self.heading_entry if hasattr(self, "heading_entry") else None))

        # ── Heading ──
        tk.Label(body, text="Heading", bg=C_WHITE, fg=C_TEXT,
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(4, 0))
        self.heading_var = tk.StringVar(value=task["heading"] if task else "")
        self.heading_entry = styled_entry(body, textvariable=self.heading_var)
        self.heading_entry.pack(fill="x", pady=(2, 10))
        if not (task and task.get("heading")):
            add_placeholder(self.heading_entry, self.heading_var, "Enter heading")

        # ── Content ──
        tk.Label(body, text="Content", bg=C_WHITE, fg=C_TEXT,
                 font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.content_text = tk.Text(
            body, font=("Segoe UI", 10), bg=C_BG, relief="flat",
            highlightbackground=C_BORDER, highlightthickness=1,
            height=4, wrap="word")
        self.content_text.pack(fill="both", expand=True, pady=(2, 10))
        if task and task.get("content"):
            self.content_text.insert("1.0", task["content"])
        else:
            add_text_placeholder(self.content_text, "Enter note")

        # ── Bottom buttons ──
        btn_bar = tk.Frame(win, bg=C_WHITE)
        btn_bar.pack(fill="x", padx=PAD, pady=(0, 18))

        cancel_btn = styled_button(
            btn_bar, "Cancel", self.win.destroy,
            bg=C_SECONDARY, fg=C_TEXT,
            hover_bg=C_BORDER, hover_fg=C_TEXT,
            font=("Segoe UI", 10), padx=16, pady=7)
        cancel_btn.pack(side="left")

        confirm_btn = styled_button(
            btn_bar, "✓  Confirm", self._confirm,
            bg=C_ACCENT, fg=C_WHITE,
            font=("Segoe UI", 10, "bold"), padx=20, pady=7)
        confirm_btn.pack(side="right")

        # Show correct row
        self._on_type_change()

    # ── Helpers ───────────────────────────────────────────────

    def _on_type_change(self):
        t = self.type_var.get()
        if t == "once":
            self.wday_row.pack_forget()
            self.date_row.pack(fill="x")
        else:
            self.date_row.pack_forget()
            self.wday_row.pack(fill="x")

    def _advance_if_done(self, current: TimeEntry, next_widget):
        if next_widget and len(current.get_time()) >= 5:
            next_widget.focus_set()

    def _autopad_date(self, _event):
        """Auto-pad month/day to 2 digits on focus-out, e.g. 2026-2-5 → 2026-02-05."""
        val = self.date_var.get().strip()
        parts = val.split("-")
        if len(parts) == 3:
            try:
                y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
                self.date_var.set(f"{y:04d}-{m:02d}-{d:02d}")
            except ValueError:
                pass

    # ── Confirm ───────────────────────────────────────────────

    def _confirm(self):
        task_type = self.type_var.get()
        start     = self.from_entry.get_time().strip()
        end       = self.to_entry.get_time().strip()
        heading   = self.heading_var.get().strip()
        if heading in ("Enter heading", ""):
            heading = ""
        content = self.content_text.get("1.0", "end-1c").strip()
        if content == "Enter note":
            content = ""

        # Determine date key
        if task_type == "weekly":
            try:
                wday_idx = WDAY_NAMES.index(self.wday_var.get()) + 1
            except ValueError:
                wday_idx = 1
            date_key = f"W{wday_idx}"
        else:
            date_key = self.date_var.get().strip()
            try:
                datetime.date.fromisoformat(date_key)
            except ValueError:
                messagebox.showerror("Invalid Date", "Please enter date as YYYY-MM-DD.",
                                     parent=self.win)
                return

        # Validate times
        try:
            time_to_min(start)
            time_to_min(end)
        except Exception:
            messagebox.showerror("Invalid Time", "Please enter times as HH:MM.",
                                 parent=self.win)
            return
        if time_to_min(start) >= time_to_min(end):
            messagebox.showerror("Invalid Time", "Start time must be before end time.",
                                 parent=self.win)
            return
        REST_PERIODS = [
            ("12:00", "13:00"),
            ("17:00", "18:00"),
            ("23:00", "23:59"),
            ("00:00", "06:00"),
        ]
        for rs, re in REST_PERIODS:
            if times_overlap(start, end, rs, re):
                messagebox.showerror(
                    "Rest Time",
                    f"This time overlaps rest period {rs}–{re}.",
                    parent=self.win
                )
                return
        if not heading:
            messagebox.showerror("Missing Heading", "Please enter a heading.",
                                 parent=self.win)
            return

        # Conflict check
        conflict = check_conflict(
            self.app.tasks, date_key, start, end, task_type,
            exclude_idx=self.editing_idx
        )
        if conflict:
            msg = (f"Time conflict with:\n\n"
                   f"  {conflict['start']}–{conflict['end']}  |  {conflict['heading']}\n\n"
                   f"Please choose a different time slot.")
            messagebox.showerror("Time Conflict", msg, parent=self.win)
            return

        new_task = {
            "date":    date_key,
            "start":   start,
            "end":     end,
            "heading": heading,
            "content": content,
            "type":    task_type,
        }

        if self.editing_idx is not None:
            self.app.tasks[self.editing_idx] = new_task
        else:
            self.app.tasks.append(new_task)

        save_tasks(self.app.tasks)
        self.app.refresh_calendar()
        self.app.refresh_next_task()
        self.win.destroy()


# ════════════════════════════════════════════════════════════════
# TASK DETAIL WINDOW
# ════════════════════════════════════════════════════════════════

class TaskDetailWindow:
    """Shows task details + countdown + edit/delete buttons."""

    def __init__(self, parent_app, task, task_idx):
        self.app      = parent_app
        self.task     = task
        self.task_idx = task_idx

        self.win = tk.Toplevel(parent_app.root)
        self.win.title("Task Detail")
        self.win.configure(bg=C_WHITE)
        self.win.resizable(False, False)
        self.win.transient(parent_app.root)   # no grab_set – allows minimize / alt-tab

        self.win.geometry("400x340")
        self.win.update_idletasks()
        rx = parent_app.root.winfo_x()
        ry = parent_app.root.winfo_y()
        rw = parent_app.root.winfo_width()
        rh = parent_app.root.winfo_height()
        self.win.geometry(f"400x340+{rx+(rw-400)//2}+{ry+(rh-340)//2}")

        self._build()
        self._update_countdown()

    # ── Build UI ──────────────────────────────────────────────

    def _build(self):
        t   = self.task
        PAD = 20
        win = self.win

        is_weekly = t.get("type") == "weekly"
        c_bg  = C_WKLY_BG if is_weekly else C_ONCE_BG
        c_bd  = C_WKLY_BD if is_weekly else C_ONCE_BD
        c_fg  = C_WKLY_FG if is_weekly else C_ONCE_FG
        badge = "🔁 Weekly" if is_weekly else "📅 One-time"

        # Heading row
        top = tk.Frame(win, bg=C_WHITE)
        top.pack(fill="x", padx=PAD, pady=(18, 4))
        tk.Label(top, text=t["heading"], bg=C_WHITE, fg=C_TEXT,
                 font=("Segoe UI", 13, "bold")).pack(side="left")
        tk.Label(top, text=badge, bg=c_bg, fg=c_fg,
                 font=("Segoe UI", 8, "bold"), padx=6, pady=2).pack(side="right")

        # Date / time bar
        if is_weekly:
            try:
                day_name = WDAY_NAMES[int(t["date"][1:]) - 1]
                date_lbl = f"Every {day_name}"
            except (ValueError, IndexError):
                date_lbl = t["date"]
        else:
            date_lbl = t["date"]

        tk.Label(win,
                 text=f"  {t['start']} – {t['end']}  ·  {date_lbl}",
                 bg=c_bg, fg=c_fg, font=("Segoe UI", 9, "bold"),
                 padx=8, pady=4
                 ).pack(anchor="w", padx=PAD)

        # Countdown
        self.countdown_var = tk.StringVar(value="")
        tk.Label(win, textvariable=self.countdown_var, bg=C_WHITE, fg=C_SUBTEXT,
                 font=("Segoe UI", 9)).pack(anchor="w", padx=PAD, pady=(4, 0))

        tk.Frame(win, bg=C_BORDER, height=1).pack(fill="x", padx=PAD, pady=8)

        # Content text
        cf = tk.Frame(win, bg=C_BG,
                      highlightbackground=C_BORDER, highlightthickness=1)
        cf.pack(fill="both", expand=True, padx=PAD)
        content_txt = tk.Text(
            cf, font=("Segoe UI", 10), bg=C_BG, relief="flat",
            fg=C_TEXT, wrap="word", height=5, padx=8, pady=8, cursor="arrow")
        content_txt.insert("1.0", t["content"] if t["content"] else "(no content)")
        content_txt.config(state="disabled")
        content_txt.pack(fill="both", expand=True)

        # Action buttons
        btn_row = tk.Frame(win, bg=C_WHITE)
        btn_row.pack(fill="x", padx=PAD, pady=(10, 16))

        styled_button(btn_row, "Delete", self._delete,
                      bg="#FEE2E2", fg="#DC2626",
                      hover_bg="#FCA5A5", hover_fg="#7F1D1D",
                      font=("Segoe UI", 9, "bold"), padx=14, pady=6
                      ).pack(side="left")

        styled_button(btn_row, "Edit", self._edit,
                      bg=C_ACCENT_LT, fg=C_ACCENT_DK,
                      font=("Segoe UI", 9, "bold"), padx=14, pady=6
                      ).pack(side="right")

    # ── Countdown ─────────────────────────────────────────────

    def _update_countdown(self):
        if not self.win.winfo_exists():
            return
        t   = self.task
        now = datetime.datetime.now()

        if t.get("type") == "weekly":
            try:
                target_wday = int(t["date"][1:])   # 1=Mon
            except (ValueError, AttributeError):
                return
            today       = datetime.date.today()
            days_ahead  = (target_wday - 1) - today.weekday()
            if days_ahead < 0:
                days_ahead += 7
            task_date = today + datetime.timedelta(days=days_ahead)
        else:
            try:
                task_date = datetime.date.fromisoformat(t["date"])
            except ValueError:
                return

        start_dt = datetime.datetime.combine(
            task_date, datetime.time(*map(int, t["start"].split(":"))))
        end_dt = datetime.datetime.combine(
            task_date, datetime.time(*map(int, t["end"].split(":"))))

        if now < start_dt:
            delta = start_dt - now
            h, rem = divmod(int(delta.total_seconds()), 3600)
            m, s   = divmod(rem, 60)
            self.countdown_var.set(f"⏳ Starts in {h:02d}:{m:02d}:{s:02d}")
        elif now <= end_dt:
            delta = end_dt - now
            h, rem = divmod(int(delta.total_seconds()), 3600)
            m, s   = divmod(rem, 60)
            self.countdown_var.set(f"▶  Ends in  {h:02d}:{m:02d}:{s:02d}")
        else:
            self.countdown_var.set("✔ Completed")
            return

        self.win.after(1000, self._update_countdown)

    # ── Actions ───────────────────────────────────────────────

    def _delete(self):
        if messagebox.askyesno("Delete", f"Delete '{self.task['heading']}'?",
                               parent=self.win):
            del self.app.tasks[self.task_idx]
            save_tasks(self.app.tasks)
            self.app.refresh_calendar()
            self.app.refresh_next_task()
            self.win.destroy()

    def _edit(self):
        self.win.destroy()
        NoteFormWindow(self.app, task=self.task, task_idx=self.task_idx)


# ════════════════════════════════════════════════════════════════
# YEAR CALENDAR WINDOW
# ════════════════════════════════════════════════════════════════

class YearCalendarWindow:
    """Month-grid calendar view for any month/year."""

    def __init__(self, parent_app):
        self.app  = parent_app
        self.win  = tk.Toplevel(parent_app.root)
        self.win.title("Yearly Calendar")
        self.win.configure(bg=C_BG)
        self.win.transient(parent_app.root)
        self.win.geometry("820x620")
        self.win.minsize(620, 480)

        now             = datetime.date.today()
        self._year_var  = tk.IntVar(value=now.year)
        self._month_var = tk.IntVar(value=now.month)

        self._build()
        self._render()

    # ── Build static UI ───────────────────────────────────────

    def _build(self):
        win = self.win

        # ── Header ──
        hdr = tk.Frame(win, bg=C_SECONDARY, pady=10)
        hdr.pack(fill="x")

        styled_button(hdr, "◀", self._prev,
                      bg=C_SECONDARY, fg=C_TEXT,
                      hover_bg=C_ACCENT_LT, hover_fg=C_ACCENT_DK,
                      font=("Segoe UI", 12, "bold"), padx=14, pady=4
                      ).pack(side="left", padx=16)

        center = tk.Frame(hdr, bg=C_SECONDARY)
        center.pack(side="left", expand=True)

        MONTHS = ["January","February","March","April","May","June",
                  "July","August","September","October","November","December"]
        self._month_cb = ttk.Combobox(
            center, values=MONTHS, state="readonly",
            font=("Segoe UI", 12), width=12)
        self._month_cb.current(self._month_var.get() - 1)
        self._month_cb.pack(side="left", padx=6)
        self._month_cb.bind("<<ComboboxSelected>>", self._on_month_sel)

        self._year_entry = styled_entry(center, textvariable=self._year_var, width=6)
        self._year_entry.config(font=("Segoe UI", 12), justify="center")
        self._year_entry.pack(side="left", padx=4)
        self._year_entry.bind("<Return>", lambda _e: self._render())
        self._year_entry.bind("<FocusOut>", lambda _e: self._render())

        styled_button(hdr, "▶", self._next,
                      bg=C_SECONDARY, fg=C_TEXT,
                      hover_bg=C_ACCENT_LT, hover_fg=C_ACCENT_DK,
                      font=("Segoe UI", 12, "bold"), padx=14, pady=4
                      ).pack(side="right", padx=16)

        # Legend
        leg = tk.Frame(hdr, bg=C_SECONDARY)
        leg.pack(side="right", padx=20)
        for color, label in (("#FB923C", "Upcoming"), ("#22C55E", "Past")):
            tk.Label(leg, text="■", bg=C_SECONDARY, fg=color,
                     font=("Segoe UI", 13)).pack(side="left")
            tk.Label(leg, text=label, bg=C_SECONDARY, fg=C_TEXT,
                     font=("Segoe UI", 9)).pack(side="left", padx=(0, 10))

        # ── Grid container ──
        self._grid_frame = tk.Frame(win, bg=C_BG)
        self._grid_frame.pack(fill="both", expand=True, padx=16, pady=12)

    # ── Navigation ────────────────────────────────────────────

    def _prev(self):
        m = self._month_var.get() - 1
        y = self._year_var.get()
        if m < 1:
            m, y = 12, y - 1
        self._month_var.set(m)
        self._year_var.set(y)
        self._month_cb.current(m - 1)
        self._render()

    def _next(self):
        m = self._month_var.get() + 1
        y = self._year_var.get()
        if m > 12:
            m, y = 1, y + 1
        self._month_var.set(m)
        self._year_var.set(y)
        self._month_cb.current(m - 1)
        self._render()

    def _on_month_sel(self, _event):
        self._month_var.set(self._month_cb.current() + 1)
        self._render()

    # ── Render ────────────────────────────────────────────────

    def _render(self):
        for w in self._grid_frame.winfo_children():
            w.destroy()

        try:
            year  = int(self._year_var.get())
            month = self._month_var.get()
        except (ValueError, tk.TclError):
            return

        today      = datetime.date.today()
        first_day  = datetime.date(year, month, 1)
        num_days   = cal_module.monthrange(year, month)[1]
        first_wday = first_day.weekday()          # 0=Mon

        g = self._grid_frame
        for col in range(7):
            g.columnconfigure(col, weight=1, minsize=80)

        # Day-name header
        for col, name in enumerate(WDAY_SHORT):
            g.rowconfigure(0, weight=0)
            tk.Label(g, text=name, bg=C_SECONDARY, fg=C_TEXT,
                     font=("Segoe UI", 10, "bold"), pady=6
                     ).grid(row=0, column=col, sticky="nsew", padx=2, pady=(0, 2))

        row = 1
        col = first_wday
        g.rowconfigure(row, weight=1, minsize=72)

        for day in range(1, num_days + 1):
            d = datetime.date(year, month, day)
            has_task = date_has_any_task(self.app.tasks, d)
            is_today = d == today

            # Pick colors
            if is_today:
                cell_bg = C_ACCENT_LT
                bdr     = C_ACCENT
            elif has_task:
                if d >= today:
                    cell_bg, bdr = "#FFEDD5", "#FDBA74"
                else:
                    cell_bg, bdr = "#DCFCE7", "#86EFAC"
            else:
                cell_bg, bdr = C_WHITE, C_BORDER

            cell = tk.Frame(g, bg=cell_bg,
                            highlightbackground=bdr, highlightthickness=1)
            cell.grid(row=row, column=col, sticky="nsew", padx=2, pady=2, ipady=10)
            g.rowconfigure(row, weight=1, minsize=72)

            num_fg = C_ACCENT_DK if is_today else C_TEXT
            tk.Label(cell, text=str(day), bg=cell_bg, fg=num_fg,
                     font=("Segoe UI", 12, "bold" if is_today else "normal")
                     ).pack(pady=(6, 0))

            if has_task:
                dot_fg = "#FB923C" if d >= today else "#22C55E"
                tk.Label(cell, text="●", bg=cell_bg, fg=dot_fg,
                         font=("Segoe UI", 9)).pack()

            col += 1
            if col > 6:
                col = 0
                row += 1
                g.rowconfigure(row, weight=1, minsize=72)

        # Fill trailing empty cells
        while col > 0 and col <= 6:
            tk.Frame(g, bg=C_BG
                     ).grid(row=row, column=col, sticky="nsew", padx=2, pady=2)
            col += 1


# ════════════════════════════════════════════════════════════════
# FLOATING ACTION BUTTON 
# ════════════════════════════════════════════════════════════════

class FloatingButton:
    """
    Internal draggable floating button (no overrideredirect).
    - Lives inside root
    - Auto hides with root
    - No topmost hacks
    - Drag within root bounds
    """

    SIZE = 58
    MARGIN = 20

    def __init__(self, parent_app):
        self.app = parent_app
        self.root = parent_app.root

        self._drag = False
        self._start_x = 0
        self._start_y = 0

        # Create button directly inside root
        self.cv = tk.Canvas(
            self.root,
            width=self.SIZE,
            height=self.SIZE,
            highlightthickness=0,
            bg=self.root["bg"],
            cursor="hand2"
        )

        self._draw()

        # Initial placement (bottom-right)
        self._place_bottom_right()

        self.cv.bind("<ButtonPress-1>", self._on_press)
        self.cv.bind("<B1-Motion>", self._on_drag)
        self.cv.bind("<ButtonRelease-1>", self._on_release)

        self._tip = None
        self.cv.bind("<Enter>", self._show_tip)
        self.cv.bind("<Leave>", self._hide_tip)

        self.cv.lift()

        self.root.bind("<Configure>", self._on_root_resize)

    # ─────────────────────────────

    def _draw(self):
        s = self.SIZE
        self.cv.delete("all")

        self.cv.create_oval(
            4, 4, s-4, s-4,
            fill="#3B82F6",
            outline=""
        )

        self.cv.create_text(
            s // 2,
            s // 2,
            text="📅",
            font=("Segoe UI", 18)
        )

    # ─────────────────────────────
    # Placement

    def _place_bottom_right(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()

        x = w - self.SIZE - self.MARGIN
        y = h - self.SIZE - self.MARGIN

        self.cv.place(x=x, y=y)

    def _on_root_resize(self, event):
        # Keep button inside bounds if window shrinks
        x = self.cv.winfo_x()
        y = self.cv.winfo_y()

        max_x = event.width - self.SIZE
        max_y = event.height - self.SIZE

        new_x = min(x, max_x)
        new_y = min(y, max_y)
        
        self.cv.place(x=new_x, y=new_y)

    # ─────────────────────────────
    # Drag

    def _on_press(self, event):
        self._drag = False
        self._start_x = event.x
        self._start_y = event.y

    def _on_drag(self, event):
        self._drag = True

        dx = event.x - self._start_x
        dy = event.y - self._start_y

        new_x = self.cv.winfo_x() + dx
        new_y = self.cv.winfo_y() + dy

        # Clamp inside root
        max_x = self.root.winfo_width() - self.SIZE
        max_y = self.root.winfo_height() - self.SIZE

        new_x = max(0, min(new_x, max_x))
        new_y = max(0, min(new_y, max_y))

        self.cv.place(x=new_x, y=new_y)

    def _on_release(self, _event):
        if not self._drag:
            YearCalendarWindow(self.app)

    # ─────────────────────────────
    # Tooltip

    def _show_tip(self, _event):
        x = self.cv.winfo_rootx()
        y = self.cv.winfo_rooty() - 34

        self._tip = tk.Toplevel(self.root)
        self._tip.overrideredirect(True)
        self._tip.geometry(f"+{x - 20}+{y}")

        tk.Label(
            self._tip,
            text="Yearly View",
            bg="#1E293B",
            fg="white",
            font=("Segoe UI", 9),
            padx=10,
            pady=5
        ).pack()

    def _hide_tip(self, _event):
        if self._tip:
            self._tip.destroy()
            self._tip = None

# ════════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ════════════════════════════════════════════════════════════════

class TimeManagerApp:

    SESSIONS = [
        ("Morning",   "06:00", "12:00"),
        ("Afternoon", "13:00", "17:00"),
        ("Evening",   "18:00", "23:00"),
    ]

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Time Manager")
        self.root.configure(bg=C_BG)
        self.root.geometry("1260x800")
        self.root.minsize(960, 600)

        self.tasks = load_tasks()

        self._build_ui()
        self._tick_clock()
        self.refresh_calendar()
        self.refresh_next_task()

        # Create floating button after window is drawn
        self.root.after(400, lambda: setattr(self, "_fab", FloatingButton(self)))

    # ════════════════════════════════════════════════════════════
    # BUILD UI
    # ════════════════════════════════════════════════════════════

    def _build_ui(self):
        # ── Top bar ──────────────────────────────────────────
        topbar = tk.Frame(self.root, bg=C_SECONDARY, height=68)
        topbar.pack(fill="x", side="top")
        topbar.pack_propagate(False)

        # Clock (left) – visible border, monospace
        clock_outer = tk.Frame(topbar, bg=C_ACCENT_DK, padx=2, pady=2)
        clock_outer.pack(side="left", padx=18, pady=12)
        clock_inner = tk.Frame(clock_outer, bg=C_WHITE)
        clock_inner.pack()
        self._clock_var = tk.StringVar(value="00:00:00")
        tk.Label(clock_inner, textvariable=self._clock_var,
                 bg=C_WHITE, fg=C_ACCENT_DK,
                 font=("Segoe UI Mono", 15, "bold"),
                 padx=14, pady=4).pack()

        # Add Note button (right)
        styled_button(topbar, "+ Add note", self._open_add,
                      bg=C_ACCENT, fg=C_WHITE,
                      font=("Segoe UI", 10, "bold"),
                      padx=20, pady=8
                      ).pack(side="right", padx=20, pady=14)

        # Next-task bar (center)
        next_bar = tk.Frame(topbar, bg=C_WHITE,
                            highlightbackground=C_BORDER, highlightthickness=1)
        next_bar.pack(side="left", expand=True, fill="both", padx=8, pady=12)
        self._next_time_var    = tk.StringVar(value="")
        self._next_heading_var = tk.StringVar(value="No upcoming task")
        tk.Label(next_bar, textvariable=self._next_time_var,
                 bg=C_WHITE, fg=C_SUBTEXT, font=("Segoe UI Mono", 10),
                 padx=12).pack(side="left")
        tk.Label(next_bar, textvariable=self._next_heading_var,
                 bg=C_WHITE, fg=C_TEXT, font=("Segoe UI", 10, "bold"),
                 padx=4).pack(side="left")

        # ── Main content ─────────────────────────────────────
        main = tk.Frame(self.root, bg=C_BG)
        main.pack(fill="both", expand=True)

        # Right sidebar – Today Overview (fixed 210px)
        sidebar = tk.Frame(main, bg=C_WHITE, width=210,
                           highlightbackground=C_BORDER, highlightthickness=1)
        sidebar.pack(side="right", fill="y", padx=(0, 8), pady=8)
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="Today Overview",
                 bg=C_WHITE, fg=C_TEXT, font=("Segoe UI", 11, "bold"),
                 pady=10).pack(fill="x", padx=12)
        tk.Frame(sidebar, bg=C_BORDER, height=1).pack(fill="x")
        self._overview_inner = tk.Frame(sidebar, bg=C_WHITE)
        self._overview_inner.pack(fill="both", expand=True, padx=8, pady=8)

        # Scrollable calendar
        cal_outer = tk.Frame(main, bg=C_BG)
        cal_outer.pack(side="left", fill="both", expand=True, padx=(8, 4), pady=8)

        self._canvas = tk.Canvas(cal_outer, bg=C_BG, highlightthickness=0)
        vsb = ttk.Scrollbar(cal_outer, orient="vertical", command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)

        self._cal_frame = tk.Frame(self._canvas, bg=C_BG)
        self._canvas_win = self._canvas.create_window(
            (0, 0), window=self._cal_frame, anchor="nw")

        self._cal_frame.bind("<Configure>", self._on_frame_cfg)
        self._canvas.bind("<Configure>", self._on_canvas_cfg)
        self._canvas.bind_all("<MouseWheel>", self._on_scroll)

    def _on_frame_cfg(self, _e):
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _on_canvas_cfg(self, e):
        self._canvas.itemconfig(self._canvas_win, width=e.width)

    def _on_scroll(self, e):
        self._canvas.yview_scroll(int(-1 * (e.delta // 120)), "units")

    # ════════════════════════════════════════════════════════════
    # CLOCK
    # ════════════════════════════════════════════════════════════

    def _tick_clock(self):
        self._clock_var.set(datetime.datetime.now().strftime("%H:%M:%S"))
        self.root.after(1000, self._tick_clock)

    # ════════════════════════════════════════════════════════════
    # NEXT TASK & TODAY OVERVIEW
    # ════════════════════════════════════════════════════════════

    def refresh_next_task(self):
        nt = get_next_task(self.tasks)
        if nt:
            self._next_time_var.set(f"  {nt['start']}–{nt['end']}  ")
            self._next_heading_var.set(nt["heading"])
        else:
            self._next_time_var.set("")
            self._next_heading_var.set("No upcoming task")
        self._refresh_overview()

    def _refresh_overview(self):
        for w in self._overview_inner.winfo_children():
            w.destroy()
        today_tasks = tasks_for_date(self.tasks, datetime.date.today().isoformat())
        if not today_tasks:
            tk.Label(self._overview_inner, text="No tasks today",
                     bg=C_WHITE, fg=C_SUBTEXT, font=("Segoe UI", 9),
                     wraplength=185, justify="center").pack(pady=12)
            return
        for t in today_tasks:
            is_w  = t.get("type") == "weekly"
            b_bg  = C_WKLY_BG if is_w else C_ONCE_BG
            b_bd  = C_WKLY_BD if is_w else C_ONCE_BD
            b_fg  = C_WKLY_FG if is_w else C_ONCE_FG
            f = tk.Frame(self._overview_inner, bg=b_bg,
                         highlightbackground=b_bd, highlightthickness=1)
            f.pack(fill="x", pady=3)
            left = tk.Frame(f, bg=b_fg, width=3)
            left.pack(side="left", fill="y")
            inner = tk.Frame(f, bg=b_bg)
            inner.pack(side="left", fill="x", expand=True, padx=6, pady=4)
            tk.Label(inner, text=f"{t['start']}–{t['end']}",
                     bg=b_bg, fg=b_fg, font=("Segoe UI", 8, "bold")).pack(anchor="w")
            tk.Label(inner, text=truncate(t["heading"], 24),
                     bg=b_bg, fg=C_TEXT, font=("Segoe UI", 9)).pack(anchor="w")

    # ════════════════════════════════════════════════════════════
    # CALENDAR RENDERING
    # ════════════════════════════════════════════════════════════

    def refresh_calendar(self):
        for w in self._cal_frame.winfo_children():
            w.destroy()

        week_dates  = get_week_dates()
        today       = datetime.date.today().isoformat()
        resolved    = resolve_tasks_for_week(self.tasks, week_dates)

        # Group tasks by resolved date
        by_date: dict[str, list] = {d: [] for d in week_dates}
        for (t, d) in resolved:
            if d in by_date:
                by_date[d].append(t)
        for d in by_date:
            by_date[d].sort(key=lambda x: time_to_min(x["start"]))

        # Column weights
        self._cal_frame.columnconfigure(0, weight=0, minsize=82)
        for i in range(7):
            self._cal_frame.columnconfigure(i + 1, weight=1, minsize=120)

        # ── Header row ──────────────────────────────────────
        corner = tk.Frame(self._cal_frame, bg=C_ACCENT_DK)
        corner.grid(row=0, column=0, sticky="nsew", padx=(0, 3), pady=(0, 4))
        tk.Label(corner, text="Session\n/ Day",
                 bg=C_ACCENT_DK, fg=C_WHITE,
                 font=("Segoe UI", 9, "bold"), justify="center",
                 padx=6, pady=8).pack(expand=True)

        for col, (day, date_str) in enumerate(zip(WDAY_SHORT, week_dates)):
            is_today = date_str == today
            hdr_bg   = C_TODAY_HDR if is_today else C_OTHER_HDR
            hdr_fg   = C_TODAY_FG  if is_today else C_OTHER_FG
            cell = tk.Frame(self._cal_frame, bg=hdr_bg,
                            highlightbackground=C_BORDER, highlightthickness=1)
            cell.grid(row=0, column=col+1, sticky="nsew", padx=2, pady=(0, 4))
            tk.Label(cell, text=day, bg=hdr_bg, fg=hdr_fg,
                     font=("Segoe UI", 10, "bold"), pady=4).pack()
            tk.Label(cell, text=date_str[8:], bg=hdr_bg, fg=hdr_fg,
                     font=("Segoe UI", 9), pady=2).pack()

        # ── Session rows ─────────────────────────────────────
        grid_row = 1
        for s_idx, (sname, ss, se) in enumerate(self.SESSIONS):
            # Large cells for session rows
            self._cal_frame.rowconfigure(grid_row, weight=4, minsize=155)

            # Session label
            tk.Label(self._cal_frame, text=sname,
                     bg=C_SECONDARY, fg=C_SUBTEXT,
                     font=("Segoe UI", 9, "bold"), justify="center",
                     wraplength=75, padx=4, pady=10
                     ).grid(row=grid_row, column=0, sticky="nsew", padx=(0, 3), pady=2)

            for col, date_str in enumerate(week_dates):
                is_today = date_str == today
                cell_bg  = "#F0F7FF"
                bdr_col  = C_BORDER
                cell = tk.Frame(self._cal_frame, bg=cell_bg,
                                highlightbackground=bdr_col, highlightthickness=1)
                cell.grid(row=grid_row, column=col+1, sticky="nsew", padx=2, pady=2)
                cell.columnconfigure(0, weight=1)

                session_tasks = [
                    t for t in by_date[date_str]
                    if times_overlap(t["start"], t["end"], ss, se)
                ]
                if session_tasks:
                    for t in session_tasks:
                        self._render_bar(cell, t, cell_bg)
                else:
                    tk.Label(cell, text="", bg=cell_bg, height=4).pack(fill="x")

            grid_row += 1

            # Rest row (thin) between sessions
            if s_idx < len(self.SESSIONS) - 1:
                self._cal_frame.rowconfigure(grid_row, weight=0, minsize=22)
                tk.Label(self._cal_frame, text="Rest",
                         bg=C_REST, fg=C_BORDER,
                         font=("Segoe UI", 8), pady=3, padx=4
                         ).grid(row=grid_row, column=0, sticky="nsew", padx=(0, 3))
                for col in range(7):
                    rf = tk.Frame(self._cal_frame, bg=C_REST)
                    rf.grid(row=grid_row, column=col+1, sticky="nsew", padx=2)
                    tk.Label(rf, bg=C_REST, height=1).pack()
                grid_row += 1

        self._refresh_overview()

    def _render_bar(self, parent, task, cell_bg):
        """Render a colored task bar inside a calendar cell."""
        idx      = self.tasks.index(task)
        is_w     = task.get("type") == "weekly"
        bar_bg   = C_WKLY_BG if is_w else C_ONCE_BG
        bar_bd   = C_WKLY_BD if is_w else C_ONCE_BD
        bar_fg   = C_WKLY_FG if is_w else C_ONCE_FG
        hover_bg = "#BFDBFE" if is_w else "#FED7AA"

        label_text = f"{task['start']}–{task['end']}\n{truncate(task['heading'], 15)}"

        bar = tk.Frame(parent, bg=bar_bg,
                       highlightbackground=bar_bd, highlightthickness=1,
                       cursor="hand2")
        bar.pack(fill="x", padx=5, pady=4)

        accent = tk.Frame(bar, bg=bar_fg, width=4)
        accent.pack(side="left", fill="y")

        lbl = tk.Label(bar, text=label_text, bg=bar_bg, fg=bar_fg,
                       font=("Segoe UI", 8), anchor="w",
                       padx=5, pady=4, justify="left")
        lbl.pack(fill="x", side="left")

        def on_click(_e, t=task, i=idx):
            TaskDetailWindow(self, t, i)

        def on_enter(_e, b=bar, l=lbl, a=accent):
            b.config(bg=hover_bg); l.config(bg=hover_bg)

        def on_leave(_e, b=bar, l=lbl, ob=bar_bg):
            b.config(bg=ob); l.config(bg=ob)

        for w in (bar, lbl, accent):
            w.bind("<Button-1>", on_click)
        bar.bind("<Enter>", on_enter);    lbl.bind("<Enter>", on_enter)
        bar.bind("<Leave>", on_leave);    lbl.bind("<Leave>", on_leave)

    # ════════════════════════════════════════════════════════════
    # OPEN ADD NOTE
    # ════════════════════════════════════════════════════════════

    def _open_add(self):
        NoteFormWindow(self)

    # ════════════════════════════════════════════════════════════
    # RUN
    # ════════════════════════════════════════════════════════════

    def run(self):
        self.root.mainloop()


# ════════════════════════════════════════════════════════════════
# ENTRY POINT
# ════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app = TimeManagerApp()
    app.run()