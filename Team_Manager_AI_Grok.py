import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from datetime import date, datetime


# ============================================================
# TEAM MANAGER — MODERN UI
# Без ИИ / Без SQL / Без интернета
# ============================================================

APP_NAME = "Team Manager"

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "team_manager_data.json"
FILES_DIR = BASE_DIR / "attachments"

FILES_DIR.mkdir(exist_ok=True)


# ============================================================
# ЦВЕТА
# ============================================================

BG = "#0B1020"
SIDEBAR = "#11182D"
CARD = "#18213A"
CARD_HOVER = "#202B49"
BORDER = "#293654"

PURPLE = "#8B5CF6"
PURPLE_DARK = "#6D28D9"
CYAN = "#06B6D4"
GREEN = "#22C55E"
ORANGE = "#F59E0B"
RED = "#EF4444"
BLUE = "#3B82F6"

WHITE = "#F8FAFC"
TEXT = "#E2E8F0"
MUTED = "#94A3B8"


# ============================================================
# JSON STORAGE
# ============================================================

class DataStore:

    def __init__(self):
        self.data = {
            "members": [],
            "tasks": [],
            "events": [],
            "notes": [],
            "next_ids": {
                "members": 1,
                "tasks": 1,
                "events": 1,
                "notes": 1
            }
        }

        self.load()

    def load(self):

        if not DATA_FILE.exists():
            self.save()
            return

        try:
            with open(
                DATA_FILE,
                "r",
                encoding="utf-8"
            ) as f:
                loaded = json.load(f)

            if isinstance(loaded, dict):
                self.data.update(loaded)

            self.data.setdefault("members", [])
            self.data.setdefault("tasks", [])
            self.data.setdefault("events", [])
            self.data.setdefault("notes", [])

            self.data.setdefault(
                "next_ids",
                {
                    "members": 1,
                    "tasks": 1,
                    "events": 1,
                    "notes": 1
                }
            )

        except Exception:

            self.data = {
                "members": [],
                "tasks": [],
                "events": [],
                "notes": [],
                "next_ids": {
                    "members": 1,
                    "tasks": 1,
                    "events": 1,
                    "notes": 1
                }
            }

            self.save()

    def save(self):

        try:

            temp = DATA_FILE.with_suffix(".tmp")

            with open(
                temp,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    self.data,
                    f,
                    ensure_ascii=False,
                    indent=4
                )

            temp.replace(DATA_FILE)

        except Exception as e:

            messagebox.showerror(
                "Ошибка сохранения",
                str(e)
            )

    def next_id(self, category):

        value = self.data["next_ids"].get(
            category,
            1
        )

        self.data["next_ids"][category] = value + 1

        return value

    def add(self, category, item):

        item["id"] = self.next_id(category)

        self.data[category].append(item)

        self.save()

        return item

    def get(self, category):

        return self.data.get(
            category,
            []
        )

    def find(self, category, item_id):

        for item in self.get(category):

            if item.get("id") == item_id:
                return item

        return None

    def update(
        self,
        category,
        item_id,
        changes
    ):

        item = self.find(
            category,
            item_id
        )

        if not item:
            return False

        item.update(changes)

        self.save()

        return True

    def delete(
        self,
        category,
        item_id
    ):

        self.data[category] = [
            x for x in self.data[category]
            if x.get("id") != item_id
        ]

        self.save()


# ============================================================
# MAIN APP
# ============================================================

class TeamManager(tk.Tk):

    def __init__(self):

        super().__init__()

        self.title(APP_NAME)

        self.geometry("1350x820")
        self.minsize(1100, 700)

        self.configure(bg=BG)

        self.store = DataStore()

        self.current_page = None

        self.setup_styles()
        self.create_ui()

        self.show_page("Главная")

        self.protocol(
            "WM_DELETE_WINDOW",
            self.close
        )

    # ========================================================
    # STYLES
    # ========================================================

    def setup_styles(self):

        style = ttk.Style()

        try:
            style.theme_use("clam")
        except:
            pass

        style.configure(
            "Treeview",
            background=CARD,
            foreground=TEXT,
            fieldbackground=CARD,
            rowheight=36,
            borderwidth=0,
            font=("Segoe UI", 10)
        )

        style.configure(
            "Treeview.Heading",
            background="#202B49",
            foreground=WHITE,
            borderwidth=0,
            font=("Segoe UI", 10, "bold"),
            padding=10
        )

        style.map(
            "Treeview",
            background=[
                ("selected", PURPLE)
            ],
            foreground=[
                ("selected", WHITE)
            ]
        )

        style.configure(
            "TCombobox",
            fieldbackground=CARD,
            background=CARD,
            foreground=TEXT
        )

    # ========================================================
    # MAIN UI
    # ========================================================

    def create_ui(self):

        self.sidebar = tk.Frame(
            self,
            bg=SIDEBAR,
            width=245
        )

        self.sidebar.pack(
            side="left",
            fill="y"
        )

        self.sidebar.pack_propagate(False)

        # Logo
        logo = tk.Frame(
            self.sidebar,
            bg=SIDEBAR
        )

        logo.pack(
            fill="x",
            padx=22,
            pady=25
        )

        tk.Label(
            logo,
            text="TM",
            bg=PURPLE,
            fg=WHITE,
            font=("Segoe UI", 18, "bold"),
            width=3,
            height=1
        ).pack(
            side="left"
        )

        logo_text = tk.Frame(
            logo,
            bg=SIDEBAR
        )

        logo_text.pack(
            side="left",
            padx=10
        )

        tk.Label(
            logo_text,
            text="TEAM",
            bg=SIDEBAR,
            fg=WHITE,
            font=("Segoe UI", 13, "bold")
        ).pack(
            anchor="w"
        )

        tk.Label(
            logo_text,
            text="MANAGER",
            bg=SIDEBAR,
            fg=PURPLE,
            font=("Segoe UI", 9, "bold")
        ).pack(
            anchor="w"
        )

        # Navigation
        self.nav_frame = tk.Frame(
            self.sidebar,
            bg=SIDEBAR
        )

        self.nav_frame.pack(
            fill="x",
            padx=12,
            pady=10
        )

        pages = [
            ("⌂", "Главная"),
            ("♟", "Команда"),
            ("✓", "Задачи"),
            ("□", "Календарь"),
            ("✎", "Заметки"),
            ("▣", "Файлы"),
            ("▥", "Статистика")
        ]

        self.nav_buttons = {}

        for icon, name in pages:

            button = tk.Button(
                self.nav_frame,
                text=f"  {icon}    {name}",
                command=lambda n=name: self.show_page(n),
                bg=SIDEBAR,
                fg=MUTED,
                activebackground=CARD_HOVER,
                activeforeground=WHITE,
                relief="flat",
                borderwidth=0,
                anchor="w",
                font=("Segoe UI", 11),
                padx=15,
                pady=13,
                cursor="hand2"
            )

            button.pack(
                fill="x",
                pady=2
            )

            self.nav_buttons[name] = button

        # Bottom
        bottom = tk.Frame(
            self.sidebar,
            bg=SIDEBAR
        )

        bottom.pack(
            side="bottom",
            fill="x",
            padx=20,
            pady=20
        )

        tk.Label(
            bottom,
            text="●  OFFLINE MODE",
            bg=SIDEBAR,
            fg=GREEN,
            font=("Segoe UI", 9, "bold")
        ).pack(
            anchor="w"
        )

        tk.Label(
            bottom,
            text="Все данные хранятся\nна этом компьютере",
            bg=SIDEBAR,
            fg=MUTED,
            justify="left",
            font=("Segoe UI", 8)
        ).pack(
            anchor="w",
            pady=(5, 0)
        )

        # Main area
        self.main = tk.Frame(
            self,
            bg=BG
        )

        self.main.pack(
            side="left",
            fill="both",
            expand=True
        )

    # ========================================================
    # PAGE SWITCH
    # ========================================================

    def show_page(self, page):

        self.current_page = page

        for name, button in self.nav_buttons.items():

            if name == page:

                button.configure(
                    bg=PURPLE,
                    fg=WHITE
                )

            else:

                button.configure(
                    bg=SIDEBAR,
                    fg=MUTED
                )

        for widget in self.main.winfo_children():
            widget.destroy()

        if page == "Главная":
            self.page_dashboard()

        elif page == "Команда":
            self.page_members()

        elif page == "Задачи":
            self.page_tasks()

        elif page == "Календарь":
            self.page_calendar()

        elif page == "Заметки":
            self.page_notes()

        elif page == "Файлы":
            self.page_files()

        elif page == "Статистика":
            self.page_statistics()

    # ========================================================
    # COMMON
    # ========================================================

    def page_header(
        self,
        title,
        subtitle
    ):

        header = tk.Frame(
            self.main,
            bg=BG
        )

        header.pack(
            fill="x",
            padx=35,
            pady=(30, 20)
        )

        tk.Label(
            header,
            text=title,
            bg=BG,
            fg=WHITE,
            font=("Segoe UI", 26, "bold")
        ).pack(
            anchor="w"
        )

        tk.Label(
            header,
            text=subtitle,
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 10)
        ).pack(
            anchor="w",
            pady=(4, 0)
        )

    def button(
        self,
        parent,
        text,
        command,
        color=PURPLE
    ):

        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=color,
            fg=WHITE,
            activebackground=PURPLE_DARK,
            activeforeground=WHITE,
            relief="flat",
            borderwidth=0,
            font=("Segoe UI", 10, "bold"),
            padx=16,
            pady=9,
            cursor="hand2"
        )

    def card(
        self,
        parent,
        title,
        value,
        color
    ):

        frame = tk.Frame(
            parent,
            bg=CARD,
            highlightbackground=BORDER,
            highlightthickness=1
        )

        frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=6
        )

        tk.Frame(
            frame,
            bg=color,
            height=4
        ).pack(
            fill="x"
        )

        tk.Label(
            frame,
            text=title,
            bg=CARD,
            fg=MUTED,
            font=("Segoe UI", 10)
        ).pack(
            anchor="w",
            padx=18,
            pady=(15, 2)
        )

        label = tk.Label(
            frame,
            text=value,
            bg=CARD,
            fg=color,
            font=("Segoe UI", 26, "bold")
        )

        label.pack(
            anchor="w",
            padx=18,
            pady=(0, 16)
        )

        return label

    # ========================================================
    # DASHBOARD
    # ========================================================

    def page_dashboard(self):

        self.page_header(
            "Добро пожаловать 👋",
            "Управляй командой, задачами и проектами в одном месте."
        )

        content = tk.Frame(
            self.main,
            bg=BG
        )

        content.pack(
            fill="both",
            expand=True,
            padx=28
        )

        # Cards
        cards = tk.Frame(
            content,
            bg=BG
        )

        cards.pack(
            fill="x",
            pady=(0, 20)
        )

        members = self.store.get("members")
        tasks = self.store.get("tasks")

        done = sum(
            x.get("status") == "Готово"
            for x in tasks
        )

        today = date.today().isoformat()

        deadlines = sum(
            x.get("status") != "Готово"
            and x.get("deadline", "")
            and x.get("deadline", "") >= today
            for x in tasks
        )

        self.card(
            cards,
            "Участники",
            len(members),
            PURPLE
        )

        self.card(
            cards,
            "Всего задач",
            len(tasks),
            CYAN
        )

        self.card(
            cards,
            "Выполнено",
            done,
            GREEN
        )

        self.card(
            cards,
            "Дедлайны",
            deadlines,
            ORANGE
        )

        # Recent tasks
        tk.Label(
            content,
            text="Ближайшие задачи",
            bg=BG,
            fg=WHITE,
            font=("Segoe UI", 16, "bold")
        ).pack(
            anchor="w",
            pady=(5, 10)
        )

        table = tk.Frame(
            content,
            bg=CARD,
            highlightbackground=BORDER,
            highlightthickness=1
        )

        table.pack(
            fill="both",
            expand=True
        )

        tree = ttk.Treeview(
            table,
            columns=(
                "title",
                "member",
                "deadline",
                "status"
            ),
            show="headings"
        )

        headers = [
            ("title", "Задача"),
            ("member", "Ответственный"),
            ("deadline", "Дедлайн"),
            ("status", "Статус")
        ]

        for col, text in headers:

            tree.heading(
                col,
                text=text
            )

        tree.column(
            "title",
            width=400
        )

        tree.column(
            "member",
            width=220
        )

        tree.column(
            "deadline",
            width=140
        )

        tree.column(
            "status",
            width=140
        )

        tree.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        active = [
            x for x in tasks
            if x.get("status") != "Готово"
        ]

        active.sort(
            key=lambda x: x.get(
                "deadline",
                ""
            )
        )

        for task in active[:10]:

            member = self.store.find(
                "members",
                task.get("member_id")
            )

            member_name = (
                member["name"]
                if member
                else "Не назначено"
            )

            tree.insert(
                "",
                "end",
                values=(
                    task.get("title", ""),
                    member_name,
                    task.get("deadline", ""),
                    task.get("status", "")
                )
            )

    # ========================================================
    # MEMBERS
    # ========================================================

    def page_members(self):

        self.page_header(
            "Команда 👥",
            "Участники проекта и их текущий прогресс."
        )

        toolbar = tk.Frame(
            self.main,
            bg=BG
        )

        toolbar.pack(
            fill="x",
            padx=35,
            pady=(0, 15)
        )

        self.button(
            toolbar,
            "+ Добавить участника",
            self.add_member
        ).pack(
            side="left"
        )

        self.button(
            toolbar,
            "Изменить прогресс",
            self.change_progress,
            CYAN
        ).pack(
            side="left",
            padx=8
        )

        self.button(
            toolbar,
            "Удалить",
            self.delete_member,
            RED
        ).pack(
            side="left"
        )

        self.members_tree = self.make_tree(
            self.main,
            [
                ("id", "ID", 60),
                ("name", "Имя", 220),
                ("role", "Роль", 220),
                ("email", "Email", 280),
                ("progress", "Прогресс", 130)
            ]
        )

        self.refresh_members()

    # ========================================================
    # TASKS
    # ========================================================

    def page_tasks(self):

        self.page_header(
            "Задачи ✓",
            "Следи за работой команды и дедлайнами."
        )

        toolbar = tk.Frame(
            self.main,
            bg=BG
        )

        toolbar.pack(
            fill="x",
            padx=35,
            pady=(0, 15)
        )

        self.button(
            toolbar,
            "+ Новая задача",
            self.add_task
        ).pack(
            side="left"
        )

        self.button(
            toolbar,
            "▶ В работу",
            self.start_task,
            CYAN
        ).pack(
            side="left",
            padx=8
        )

        self.button(
            toolbar,
            "✓ Выполнить",
            self.complete_task,
            GREEN
        ).pack(
            side="left"
        )

        self.button(
            toolbar,
            "Удалить",
            self.delete_task,
            RED
        ).pack(
            side="left",
            padx=8
        )

        self.tasks_tree = self.make_tree(
            self.main,
            [
                ("id", "ID", 55),
                ("title", "Задача", 350),
                ("member", "Ответственный", 200),
                ("priority", "Приоритет", 130),
                ("deadline", "Дедлайн", 130),
                ("status", "Статус", 130)
            ]
        )

        self.refresh_tasks()

    # ========================================================
    # CALENDAR
    # ========================================================

    def page_calendar(self):

        self.page_header(
            "Календарь 📅",
            "События, контрольные, встречи и важные даты."
        )

        toolbar = tk.Frame(
            self.main,
            bg=BG
        )

        toolbar.pack(
            fill="x",
            padx=35,
            pady=(0, 15)
        )

        self.button(
            toolbar,
            "+ Новое событие",
            self.add_event
        ).pack(
            side="left"
        )

        self.button(
            toolbar,
            "Удалить",
            self.delete_event,
            RED
        ).pack(
            side="left",
            padx=8
        )

        self.events_tree = self.make_tree(
            self.main,
            [
                ("id", "ID", 55),
                ("date", "Дата", 120),
                ("time", "Время", 100),
                ("title", "Название", 260),
                ("type", "Тип", 150),
                ("description", "Описание", 400)
            ]
        )

        self.refresh_events()

    # ========================================================
    # NOTES
    # ========================================================

    def page_notes(self):

        self.page_header(
            "Заметки 📝",
            "Храни идеи, планы и важную информацию."
        )

        toolbar = tk.Frame(
            self.main,
            bg=BG
        )

        toolbar.pack(
            fill="x",
            padx=35,
            pady=(0, 15)
        )

        self.button(
            toolbar,
            "+ Новая заметка",
            self.add_note
        ).pack(
            side="left"
        )

        self.button(
            toolbar,
            "Удалить",
            self.delete_note,
            RED
        ).pack(
            side="left",
            padx=8
        )

        self.notes_tree = self.make_tree(
            self.main,
            [
                ("id", "ID", 60),
                ("title", "Название", 500),
                ("date", "Создано", 300)
            ]
        )

        self.notes_tree.bind(
            "<Double-1>",
            self.open_note
        )

        self.refresh_notes()

    # ========================================================
    # FILES
    # ========================================================

    def page_files(self):

        self.page_header(
            "Файлы 📎",
            "Файлы проекта хранятся в папке attachments."
        )

        toolbar = tk.Frame(
            self.main,
            bg=BG
        )

        toolbar.pack(
            fill="x",
            padx=35,
            pady=(0, 15)
        )

        self.button(
            toolbar,
            "+ Добавить файл",
            self.add_file
        ).pack(
            side="left"
        )

        self.button(
            toolbar,
            "📂 Открыть папку",
            self.open_files_folder,
            CYAN
        ).pack(
            side="left",
            padx=8
        )

        self.button(
            toolbar,
            "Удалить",
            self.delete_file,
            RED
        ).pack(
            side="left"
        )

        frame = tk.Frame(
            self.main,
            bg=CARD,
            highlightbackground=BORDER,
            highlightthickness=1
        )

        frame.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=(0, 30)
        )

        self.files_list = tk.Listbox(
            frame,
            bg=CARD,
            fg=TEXT,
            selectbackground=PURPLE,
            selectforeground=WHITE,
            font=("Segoe UI", 11),
            borderwidth=0,
            highlightthickness=0
        )

        self.files_list.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=15
        )

        self.files_list.bind(
            "<Double-1>",
            self.open_file
        )

        self.refresh_files()

    # ========================================================
    # STATISTICS
    # ========================================================

    def page_statistics(self):

        self.page_header(
            "Статистика 📊",
            "Общая информация о проекте."
        )

        frame = tk.Frame(
            self.main,
            bg=CARD,
            highlightbackground=BORDER,
            highlightthickness=1
        )

        frame.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=(0, 30)
        )

        members = self.store.get("members")
        tasks = self.store.get("tasks")

        total = len(tasks)

        done = sum(
            x.get("status") == "Готово"
            for x in tasks
        )

        work = sum(
            x.get("status") == "В работе"
            for x in tasks
        )

        new = sum(
            x.get("status") == "Новая"
            for x in tasks
        )

        overdue = 0

        today = date.today().isoformat()

        for task in tasks:

            deadline = task.get(
                "deadline",
                ""
            )

            if (
                deadline
                and deadline < today
                and task.get("status") != "Готово"
            ):
                overdue += 1

        percent = (
            round(done / total * 100)
            if total
            else 0
        )

        text = f"""
        TEAM MANAGER
        ─────────────────────────────────────

        👥 Участников              {len(members)}

        📋 Всего задач             {total}

        🆕 Новых задач             {new}

        🔵 В работе                {work}

        🟢 Выполнено               {done}

        🔴 Просрочено              {overdue}


        ОБЩИЙ ПРОГРЕСС

        {"█" * (percent // 5)}{"░" * (20 - percent // 5)}

        {percent}%


        Данные хранятся локально в:

        {DATA_FILE.name}
        """

        tk.Label(
            frame,
            text=text,
            bg=CARD,
            fg=TEXT,
            justify="left",
            anchor="nw",
            font=("Consolas", 13),
            padx=35,
            pady=30
        ).pack(
            fill="both",
            expand=True
        )

    # ========================================================
    # TREEVIEW
    # ========================================================

    def make_tree(
        self,
        parent,
        columns
    ):

        frame = tk.Frame(
            parent,
            bg=CARD,
            highlightbackground=BORDER,
            highlightthickness=1
        )

        frame.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=(0, 30)
        )

        tree = ttk.Treeview(
            frame,
            columns=[
                x[0] for x in columns
            ],
            show="headings"
        )

        for column, title, width in columns:

            tree.heading(
                column,
                text=title
            )

            tree.column(
                column,
                width=width,
                minwidth=50
            )

        scrollbar = ttk.Scrollbar(
            frame,
            orient="vertical",
            command=tree.yview
        )

        tree.configure(
            yscrollcommand=scrollbar.set
        )

        tree.pack(
            side="left",
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        scrollbar.pack(
            side="right",
            fill="y",
            pady=10
        )

        return tree

    # ========================================================
    # MEMBERS
    # ========================================================

    def refresh_members(self):

        for x in self.members_tree.get_children():
            self.members_tree.delete(x)

        for member in self.store.get("members"):

            self.members_tree.insert(
                "",
                "end",
                values=(
                    member["id"],
                    member.get("name", ""),
                    member.get("role", ""),
                    member.get("email", ""),
                    f'{member.get("progress", 0)}%'
                )
            )

    def add_member(self):

        name = simpledialog.askstring(
            "Новый участник",
            "Имя:"
        )

        if not name:
            return

        role = simpledialog.askstring(
            "Новый участник",
            "Роль:"
        ) or ""

        email = simpledialog.askstring(
            "Новый участник",
            "Email:"
        ) or ""

        self.store.add(
            "members",
            {
                "name": name,
                "role": role,
                "email": email,
                "progress": 0
            }
        )

        self.refresh_members()

    def change_progress(self):

        selected = self.members_tree.selection()

        if not selected:
            messagebox.showwarning(
                "Внимание",
                "Выбери участника."
            )
            return

        values = self.members_tree.item(
            selected[0]
        )["values"]

        member_id = int(values[0])

        progress = simpledialog.askinteger(
            "Прогресс",
            "Введите значение от 0 до 100:",
            minvalue=0,
            maxvalue=100,
            initialvalue=int(
                str(values[4]).replace("%", "")
            )
        )

        if progress is not None:

            self.store.update(
                "members",
                member_id,
                {
                    "progress": progress
                }
            )

            self.refresh_members()

    def delete_member(self):

        selected = self.members_tree.selection()

        if not selected:
            return

        member_id = int(
            self.members_tree.item(
                selected[0]
            )["values"][0]
        )

        if messagebox.askyesno(
            "Удаление",
            "Удалить участника?"
        ):

            self.store.delete(
                "members",
                member_id
            )

            for task in self.store.get("tasks"):

                if task.get("member_id") == member_id:
                    task["member_id"] = None

            self.store.save()

            self.refresh_members()

    # ========================================================
    # TASKS
    # ========================================================

    def refresh_tasks(self):

        for x in self.tasks_tree.get_children():
            self.tasks_tree.delete(x)

        tasks = list(
            self.store.get("tasks")
        )

        tasks.sort(
            key=lambda x: (
                x.get("status") == "Готово",
                x.get("deadline", "")
            )
        )

        for task in tasks:

            member = self.store.find(
                "members",
                task.get("member_id")
            )

            name = (
                member["name"]
                if member
                else "Не назначено"
            )

            self.tasks_tree.insert(
                "",
                "end",
                values=(
                    task["id"],
                    task.get("title", ""),
                    name,
                    task.get("priority", ""),
                    task.get("deadline", ""),
                    task.get("status", "")
                )
            )

    def selected_task(self):

        selected = self.tasks_tree.selection()

        if not selected:
            return None

        return int(
            self.tasks_tree.item(
                selected[0]
            )["values"][0]
        )

    def add_task(self):

        dialog = TaskDialog(
            self,
            self.store
        )

        self.wait_window(dialog)

        if not dialog.result:
            return

        title, description, member_id, priority, deadline = dialog.result

        self.store.add(
            "tasks",
            {
                "title": title,
                "description": description,
                "member_id": member_id,
                "priority": priority,
                "deadline": deadline,
                "status": "Новая",
                "created_at": datetime.now().isoformat()
            }
        )

        self.refresh_tasks()

    def start_task(self):

        task_id = self.selected_task()

        if task_id is None:
            return

        self.store.update(
            "tasks",
            task_id,
            {
                "status": "В работе"
            }
        )

        self.refresh_tasks()

    def complete_task(self):

        task_id = self.selected_task()

        if task_id is None:
            return

        self.store.update(
            "tasks",
            task_id,
            {
                "status": "Готово"
            }
        )

        self.refresh_tasks()

    def delete_task(self):

        task_id = self.selected_task()

        if task_id is None:
            return

        if messagebox.askyesno(
            "Удаление",
            "Удалить задачу?"
        ):

            self.store.delete(
                "tasks",
                task_id
            )

            self.refresh_tasks()

    # ========================================================
    # EVENTS
    # ========================================================

    def refresh_events(self):

        for x in self.events_tree.get_children():
            self.events_tree.delete(x)

        events = sorted(
            self.store.get("events"),
            key=lambda x: (
                x.get("event_date", ""),
                x.get("event_time", "")
            )
        )

        for event in events:

            self.events_tree.insert(
                "",
                "end",
                values=(
                    event["id"],
                    event.get("event_date", ""),
                    event.get("event_time", ""),
                    event.get("title", ""),
                    event.get("event_type", ""),
                    event.get("description", "")
                )
            )

    def add_event(self):

        dialog = EventDialog(self)

        self.wait_window(dialog)

        if not dialog.result:
            return

        title, event_date, event_time, event_type, description = dialog.result

        self.store.add(
            "events",
            {
                "title": title,
                "event_date": event_date,
                "event_time": event_time,
                "event_type": event_type,
                "description": description
            }
        )

        self.refresh_events()

    def delete_event(self):

        selected = self.events_tree.selection()

        if not selected:
            return

        event_id = int(
            self.events_tree.item(
                selected[0]
            )["values"][0]
        )

        self.store.delete(
            "events",
            event_id
        )

        self.refresh_events()

    # ========================================================
    # NOTES
    # ========================================================

    def refresh_notes(self):

        for x in self.notes_tree.get_children():
            self.notes_tree.delete(x)

        for note in reversed(
            self.store.get("notes")
        ):

            self.notes_tree.insert(
                "",
                "end",
                values=(
                    note["id"],
                    note.get("title", ""),
                    note.get("created_at", "")
                )
            )

    def add_note(self):

        dialog = NoteDialog(self)

        self.wait_window(dialog)

        if not dialog.result:
            return

        title, content = dialog.result

        self.store.add(
            "notes",
            {
                "title": title,
                "content": content,
                "created_at": datetime.now().strftime(
                    "%Y-%m-%d %H:%M"
                )
            }
        )

        self.refresh_notes()

    def delete_note(self):

        selected = self.notes_tree.selection()

        if not selected:
            return

        note_id = int(
            self.notes_tree.item(
                selected[0]
            )["values"][0]
        )

        self.store.delete(
            "notes",
            note_id
        )

        self.refresh_notes()

    def open_note(self, event=None):

        selected = self.notes_tree.selection()

        if not selected:
            return

        note_id = int(
            self.notes_tree.item(
                selected[0]
            )["values"][0]
        )

        note = self.store.find(
            "notes",
            note_id
        )

        if note:
            NoteViewer(
                self,
                note["title"],
                note["content"]
            )

    # ========================================================
    # FILES
    # ========================================================

    def refresh_files(self):

        self.files_list.delete(
            0,
            tk.END
        )

        for file in sorted(
            FILES_DIR.iterdir(),
            key=lambda x: x.name.lower()
        ):

            if file.is_file():

                self.files_list.insert(
                    tk.END,
                    file.name
                )

    def add_file(self):

        filename = filedialog.askopenfilename()

        if not filename:
            return

        source = Path(filename)
        target = FILES_DIR / source.name

        if target.exists():

            if not messagebox.askyesno(
                "Файл существует",
                "Заменить существующий файл?"
            ):
                return

        try:

            shutil.copy2(
                source,
                target
            )

            self.refresh_files()

        except Exception as e:

            messagebox.showerror(
                "Ошибка",
                str(e)
            )

    def delete_file(self):

        selected = self.files_list.curselection()

        if not selected:
            return

        name = self.files_list.get(
            selected[0]
        )

        if messagebox.askyesno(
            "Удаление",
            f"Удалить {name}?"
        ):

            try:

                (FILES_DIR / name).unlink()

                self.refresh_files()

            except Exception as e:

                messagebox.showerror(
                    "Ошибка",
                    str(e)
                )

    def open_file(self, event=None):

        selected = self.files_list.curselection()

        if not selected:
            return

        path = (
            FILES_DIR /
            self.files_list.get(selected[0])
        )

        try:

            if os.name == "nt":
                os.startfile(str(path))

            elif sys.platform == "darwin":
                subprocess.Popen(
                    ["open", str(path)]
                )

            else:
                subprocess.Popen(
                    ["xdg-open", str(path)]
                )

        except Exception as e:

            messagebox.showerror(
                "Ошибка",
                str(e)
            )

    def open_files_folder(self):

        try:

            if os.name == "nt":
                os.startfile(str(FILES_DIR))

            elif sys.platform == "darwin":
                subprocess.Popen(
                    ["open", str(FILES_DIR)]
                )

            else:
                subprocess.Popen(
                    ["xdg-open", str(FILES_DIR)]
                )

        except Exception as e:

            messagebox.showerror(
                "Ошибка",
                str(e)
            )

    # ========================================================
    # CLOSE
    # ========================================================

    def close(self):

        self.store.save()

        self.destroy()


# ============================================================
# TASK DIALOG
# ============================================================

class TaskDialog(tk.Toplevel):

    def __init__(
        self,
        parent,
        store
    ):

        super().__init__(parent)

        self.store = store
        self.result = None

        self.title("Новая задача")
        self.geometry("540x620")

        self.configure(bg=BG)

        self.transient(parent)
        self.grab_set()

        frame = tk.Frame(
            self,
            bg=BG
        )

        frame.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=25
        )

        self.label(frame, "Название")

        self.title_entry = self.entry(frame)

        self.label(frame, "Описание")

        self.description = tk.Text(
            frame,
            height=6,
            bg=CARD,
            fg=TEXT,
            insertbackground=WHITE,
            relief="flat",
            font=("Segoe UI", 10)
        )

        self.description.pack(
            fill="x",
            pady=(5, 18)
        )

        self.label(frame, "Ответственный")

        members = self.store.get("members")

        self.member_map = {
            x["name"]: x["id"]
            for x in members
        }

        self.member = ttk.Combobox(
            frame,
            values=list(
                self.member_map.keys()
            ),
            state="readonly"
        )

        self.member.pack(
            fill="x",
            pady=(5, 18)
        )

        self.label(frame, "Приоритет")

        self.priority = ttk.Combobox(
            frame,
            values=[
                "Низкий",
                "Средний",
                "Высокий",
                "Критический"
            ],
            state="readonly"
        )

        self.priority.set("Средний")

        self.priority.pack(
            fill="x",
            pady=(5, 18)
        )

        self.label(frame, "Дедлайн YYYY-MM-DD")

        self.deadline = self.entry(frame)

        self.deadline.insert(
            0,
            date.today().isoformat()
        )

        self.button(
            frame,
            "Создать задачу",
            self.submit
        ).pack(
            pady=25
        )

    def label(
        self,
        parent,
        text
    ):

        tk.Label(
            parent,
            text=text,
            bg=BG,
            fg=TEXT,
            font=("Segoe UI", 10, "bold")
        ).pack(
            anchor="w"
        )

    def entry(self, parent):

        entry = tk.Entry(
            parent,
            bg=CARD,
            fg=TEXT,
            insertbackground=WHITE,
            relief="flat",
            font=("Segoe UI", 10)
        )

        entry.pack(
            fill="x",
            pady=(5, 18),
            ipady=8
        )

        return entry

    def button(
        self,
        parent,
        text,
        command
    ):

        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=PURPLE,
            fg=WHITE,
            activebackground=PURPLE_DARK,
            activeforeground=WHITE,
            relief="flat",
            borderwidth=0,
            font=("Segoe UI", 10, "bold"),
            padx=20,
            pady=10,
            cursor="hand2"
        )

    def submit(self):

        title = self.title_entry.get().strip()

        if not title:
            messagebox.showwarning(
                "Ошибка",
                "Введите название."
            )
            return

        deadline = self.deadline.get().strip()

        try:

            datetime.strptime(
                deadline,
                "%Y-%m-%d"
            )

        except ValueError:

            messagebox.showwarning(
                "Ошибка",
                "Введите дату в формате YYYY-MM-DD."
            )

            return

        self.result = (
            title,
            self.description.get(
                "1.0",
                tk.END
            ).strip(),
            self.member_map.get(
                self.member.get()
            ),
            self.priority.get(),
            deadline
        )

        self.destroy()


# ============================================================
# EVENT DIALOG
# ============================================================

class EventDialog(tk.Toplevel):

    def __init__(self, parent):

        super().__init__(parent)

        self.result = None

        self.title("Новое событие")
        self.geometry("520x570")

        self.configure(bg=BG)

        self.transient(parent)
        self.grab_set()

        frame = tk.Frame(
            self,
            bg=BG
        )

        frame.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=25
        )

        self.label(frame, "Название")

        self.title_entry = self.entry(frame)

        self.label(frame, "Дата YYYY-MM-DD")

        self.date_entry = self.entry(frame)

        self.date_entry.insert(
            0,
            date.today().isoformat()
        )

        self.label(frame, "Время")

        self.time_entry = self.entry(frame)

        self.time_entry.insert(
            0,
            "12:00"
        )

        self.label(frame, "Тип")

        self.type_box = ttk.Combobox(
            frame,
            values=[
                "Учёба",
                "Контрольная",
                "Экзамен",
                "Проект",
                "Встреча",
                "Другое"
            ],
            state="readonly"
        )

        self.type_box.set("Учёба")

        self.type_box.pack(
            fill="x",
            pady=(5, 18)
        )

        self.label(frame, "Описание")

        self.description = tk.Text(
            frame,
            height=5,
            bg=CARD,
            fg=TEXT,
            insertbackground=WHITE,
            relief="flat"
        )

        self.description.pack(
            fill="x",
            pady=(5, 20)
        )

        self.button(
            frame,
            "Добавить",
            self.submit
        ).pack()

    def label(self, parent, text):

        tk.Label(
            parent,
            text=text,
            bg=BG,
            fg=TEXT,
            font=("Segoe UI", 10, "bold")
        ).pack(
            anchor="w"
        )

    def entry(self, parent):

        e = tk.Entry(
            parent,
            bg=CARD,
            fg=TEXT,
            insertbackground=WHITE,
            relief="flat"
        )

        e.pack(
            fill="x",
            pady=(5, 15),
            ipady=7
        )

        return e

    def button(
        self,
        parent,
        text,
        command
    ):

        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=PURPLE,
            fg=WHITE,
            activebackground=PURPLE_DARK,
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            padx=20,
            pady=10
        )

    def submit(self):

        title = self.title_entry.get().strip()

        if not title:
            return

        event_date = self.date_entry.get().strip()

        try:

            datetime.strptime(
                event_date,
                "%Y-%m-%d"
            )

        except ValueError:

            messagebox.showwarning(
                "Ошибка",
                "Неверная дата."
            )

            return

        self.result = (
            title,
            event_date,
            self.time_entry.get().strip(),
            self.type_box.get(),
            self.description.get(
                "1.0",
                tk.END
            ).strip()
        )

        self.destroy()


# ============================================================
# NOTE DIALOG
# ============================================================

class NoteDialog(tk.Toplevel):

    def __init__(self, parent):

        super().__init__(parent)

        self.result = None

        self.title("Новая заметка")
        self.geometry("720x620")

        self.configure(bg=BG)

        self.transient(parent)
        self.grab_set()

        frame = tk.Frame(
            self,
            bg=BG
        )

        frame.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=25
        )

        tk.Label(
            frame,
            text="Название",
            bg=BG,
            fg=TEXT,
            font=("Segoe UI", 10, "bold")
        ).pack(
            anchor="w"
        )

        self.title_entry = tk.Entry(
            frame,
            bg=CARD,
            fg=TEXT,
            insertbackground=WHITE,
            relief="flat"
        )

        self.title_entry.pack(
            fill="x",
            pady=(5, 20),
            ipady=8
        )

        tk.Label(
            frame,
            text="Текст заметки",
            bg=BG,
            fg=TEXT,
            font=("Segoe UI", 10, "bold")
        ).pack(
            anchor="w"
        )

        self.text = tk.Text(
            frame,
            bg=CARD,
            fg=TEXT,
            insertbackground=WHITE,
            relief="flat",
            wrap="word",
            font=("Segoe UI", 11)
        )

        self.text.pack(
            fill="both",
            expand=True,
            pady=(5, 20)
        )

        tk.Button(
            frame,
            text="Сохранить",
            command=self.submit,
            bg=PURPLE,
            fg=WHITE,
            activebackground=PURPLE_DARK,
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            padx=25,
            pady=10
        ).pack()

    def submit(self):

        title = self.title_entry.get().strip()

        if not title:
            return

        self.result = (
            title,
            self.text.get(
                "1.0",
                tk.END
            ).strip()
        )

        self.destroy()


# ============================================================
# NOTE VIEWER
# ============================================================

class NoteViewer(tk.Toplevel):

    def __init__(
        self,
        parent,
        title,
        content
    ):

        super().__init__(parent)

        self.title(title)
        self.geometry("800x650")
        self.configure(bg=BG)

        text = tk.Text(
            self,
            bg=CARD,
            fg=TEXT,
            insertbackground=WHITE,
            relief="flat",
            wrap="word",
            font=("Segoe UI", 11),
            padx=25,
            pady=25
        )

        text.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=25
        )

        text.insert(
            "1.0",
            content
        )

        text.config(
            state="disabled"
        )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    app = TeamManager()

    app.mainloop()