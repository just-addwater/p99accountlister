import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.font import Font
import json
import os
import platform

class actlist:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Account Lister")
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.95)
        self.root.resizable(True, True)
        self.root.configure(bg='#2c2c2c')

        style = ttk.Style(self.root)
        style.theme_use('clam')
        style.configure("TCombobox", fieldbackground="#555", background="#555", foreground="white", selectbackground="#444")
        style.configure("TScrollbar", background="#444", troughcolor="#2c2c2c", bordercolor="#2c2c2c", arrowcolor="white")

        self.accounts = []
        self.recent_characters = []
        self.selected_server = "All"
        self.window_position = {"x": 1000, "y": 100}
        self.eq_classes = ["Bard", "Cleric", "Druid", "Enchanter", "Magician", "Monk", "Necromancer",
                         "Paladin", "Ranger", "Rogue", "Shadow Knight", "Shaman", "Warrior", "Wizard"]
        self.expanded_classes = {cls: True for cls in self.eq_classes}
        self.character_widgets = []

        self.server_colors = {"Blue": "#4da6ff", "Green": "#4dff4d", "Red": "#ff4d4d", "All": "#ffffff"}

        self.load_data()
        self.setup_window()
        self.setup_ui()
        self.refresh_character_list()

        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)

    def setup_window(self):
        width, height = 420, 700
        x, y = self.window_position.get("x", 1000), self.window_position.get("y", 100)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.root.minsize(350, 700)

    def load_data(self):
        if os.path.exists("act.txt"):
            try:
                with open("act.txt", "r") as f:
                    data = json.load(f)
                    self.accounts = data.get("accounts", [])
                    self.recent_characters = data.get("recent", [])
                    self.selected_server = data.get("last_server", "All")
                    self.window_position = data.get("window_position", {"x": 1000, "y": 100})
                    self.expanded_classes = data.get("expanded_classes", self.expanded_classes)
            except (json.JSONDecodeError, FileNotFoundError):
                self.create_default_file()
        else:
            self.create_default_file()

    def create_default_file(self):
        default_data = {
            "accounts": [], "recent": [], "last_server": "All",
            "window_position": {"x": 1000, "y": 100},
            "expanded_classes": self.expanded_classes
        }
        with open("act.txt", "w") as f:
            json.dump(default_data, f, indent=4)

    def save_data(self):
        data = {
            "accounts": self.accounts,
            "recent": self.recent_characters[-3:],
            "last_server": self.selected_server,
            "window_position": {"x": self.root.winfo_x(), "y": self.root.winfo_y()},
            "expanded_classes": self.expanded_classes
        }
        with open("act.txt", "w") as f:
            json.dump(data, f, indent=4)

    def setup_ui(self):
        top_frame = tk.Frame(self.root, bg='#2c2c2c')
        top_frame.pack(fill='x', padx=10, pady=(5, 0))
        tk.Label(top_frame, text="P99 Account List", font=("Arial", 16, "bold"), bg='#2c2c2c', fg='white').pack(pady=(0, 8))
        filter_frame = tk.Frame(top_frame, bg='#2c2c2c')
        filter_frame.pack(fill='x')
        self.server_var = tk.StringVar(value=self.selected_server)
        for server in ["All", "Blue", "Green", "Red"]:
            rb = tk.Radiobutton(filter_frame, text=server, variable=self.server_var, value=server,
                                 command=self.on_server_change, font=("Arial", 11, "bold"),
                                 bg='#2c2c2c', fg=self.server_colors[server], selectcolor='#404040',
                                 activebackground='#2c2c2c', activeforeground=self.server_colors[server],
                                 indicatoron=0, relief='raised', bd=2)
            rb.pack(side='left', padx=5, expand=True, fill='x')
        self.setup_scrollable_frame()
        button_frame = tk.Frame(self.root, bg='#2c2c2c')
        button_frame.pack(fill='x', padx=10, pady=8)
        tk.Button(button_frame, text="Add Character", command=self.add_character_dialog,
                             bg='#0078D7', fg='white', font=("Arial", 10, "bold"), relief='raised', bd=2).pack(side='left', expand=True, fill='x', padx=5)
        tk.Button(button_frame, text="Exit", command=self.on_exit,
                              bg='#555555', fg='white', font=("Arial", 10), relief='raised', bd=2).pack(side='right', expand=True, fill='x', padx=5)

    def setup_scrollable_frame(self):
        canvas_frame = tk.Frame(self.root, bg='#2c2c2c')
        canvas_frame.pack(fill='both', expand=True, padx=10, pady=5)
        self.canvas = tk.Canvas(canvas_frame, bg='#2c2c2c', highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg='#2c2c2c')
        
        # This binding ensures the frame inside the canvas is always the width of the canvas
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.root.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def on_server_change(self):
        self.selected_server = self.server_var.get()
        self.refresh_character_list()

    def refresh_character_list(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.character_widgets.clear()
        
        filtered_accounts = [acc for acc in self.accounts if self.selected_server == "All" or acc["server"] == self.selected_server]
        recent_chars_data = [next((acc for acc in self.accounts if acc["name"] == name), None) for name in reversed(self.recent_characters)]
        recent_chars_data = [char for char in recent_chars_data if char and (self.selected_server == "All" or char["server"] == self.selected_server)]

        if recent_chars_data:
            tk.Label(self.scrollable_frame, text="Recent", font=("Arial", 14, "bold"), bg='#2c2c2c', fg='#ffff4d').pack(anchor='w', pady=(0, 8))
            for char_data in recent_chars_data:
                self.create_character_widget(char_data, is_recent=True)

        class_groups = {cls: [] for cls in self.eq_classes}
        for account in filtered_accounts:
            class_groups[account["class"]].append(account)

        for eq_class in self.eq_classes:
            characters = class_groups[eq_class]
            class_header_frame = tk.Frame(self.scrollable_frame, bg='#2c2c2c')
            class_header_frame.pack(fill='x', pady=(10, 2))
            is_expanded = self.expanded_classes.get(eq_class, True)
            arrow = "▼" if is_expanded else "▶"
            fg_color = '#ffffff' if characters else '#666666'
            class_text = f"{arrow} {eq_class} ({len(characters)})"
            class_label = tk.Label(class_header_frame, text=class_text, font=("Arial", 12, "bold"), bg='#2c2c2c', fg=fg_color, cursor="hand2")
            class_label.pack(anchor='w')
            class_label.bind("<Button-1>", lambda e, cls=eq_class: self.toggle_class_expansion(cls))
            if is_expanded:
                for character in sorted(characters, key=lambda c: c['name']):
                    self.create_character_widget(character)
        
        # FIX 2: Smartly resize window to fit the widest entry, up to a max limit
        self.autosize_window_width(filtered_accounts)

    def autosize_window_width(self, accounts):
        max_pixel_width = 0
        bold_font = Font(family="Arial", size=11, weight="bold")
        
        for acc in accounts:
            # We only need to measure the longest text string
            text = f"{acc['name']} (Lvl {acc['level']})"
            width = bold_font.measure(text)
            if width > max_pixel_width:
                max_pixel_width = width
        
        # Add padding for server name, scrollbar, margins etc.
        required_width = max_pixel_width + 160
        
        # Enforce a reasonable maximum width
        capped_width = min(required_width, 600)
        
        current_width = self.root.winfo_width()
        if capped_width > current_width:
            self.root.geometry(f"{capped_width}x{self.root.winfo_height()}")

    def toggle_class_expansion(self, eq_class):
        self.expanded_classes[eq_class] = not self.expanded_classes.get(eq_class, True)
        self.refresh_character_list()

    def create_character_widget(self, character, is_recent=False):
        char_frame = tk.Frame(self.scrollable_frame, bg='#404040', relief='solid', bd=1)
        char_frame.pack(fill='x', padx=5, pady=3)
        info_line = tk.Frame(char_frame, bg='#404040')
        info_line.pack(fill='x', padx=8, pady=(5,0))

        # FIX 1: Use grid layout to prevent width changes on bolding
        info_line.grid_columnconfigure(0, weight=1) # Column 0 expands
        info_line.grid_columnconfigure(1, weight=0) # Column 1 is fixed size

        info_text = f"{character['name']} - {character['class']} (Lvl {character['level']})" if is_recent else f"{character['name']} (Lvl {character['level']})"
        char_label = tk.Label(info_line, text=info_text, font=("Arial", 11), bg='#404040', fg='white', anchor='w')
        char_label.grid(row=0, column=0, sticky='ew')
        server_label = tk.Label(info_line, text=character["server"], font=("Arial", 10, "bold"), bg='#404040', fg=self.server_colors[character["server"]], anchor='e')
        server_label.grid(row=0, column=1, sticky='e', padx=(10,0))

        note_label = None
        if character.get("note"):
            note_label = tk.Label(char_frame, text=character['note'], font=("Arial", 9, "italic"), bg='#404040', fg='#ccc', anchor='w')
            note_label.pack(fill='x', padx=8)

        cred_container = tk.Frame(char_frame, bg='#404040', height=65)
        cred_container.pack(fill='x', padx=8, pady=(5,5))
        cred_container.pack_propagate(False)

        username_label = tk.Label(cred_container, text=f"User: {character['username']}", font=("Consolas", 12, "bold"), bg='#404040', fg='white', anchor='w')
        username_label.pack(fill='x')
        password_label = tk.Label(cred_container, text=f"Pass: {character['password']}", font=("Consolas", 12, "bold"), bg='#404040', fg='white', anchor='w')
        password_label.pack(fill='x')

        widget_info = { 'frame': char_frame, 'info_line': info_line, 'char_label': char_label, 'server_label': server_label, 
                        'cred_container': cred_container, 'user_label': username_label, 'pass_label': password_label, 'note_label': note_label }
        self.character_widgets.append(widget_info)

        def on_click(event): self.on_character_click(character, widget_info)

        for widget in [char_frame, info_line, char_label, server_label, cred_container, username_label, password_label]:
            widget.bind("<Button-1>", on_click); widget.configure(cursor="hand2")
        if note_label: note_label.bind("<Button-1>", on_click); note_label.configure(cursor="hand2")

    def on_character_click(self, character, clicked_widget_info):
        for info in self.character_widgets:
            is_selected = (info == clicked_widget_info)
            bg_color = '#005a9e' if is_selected else '#404040'
            fg_color = '#ffffff' if is_selected else '#aaaaaa'
            info_font = ("Arial", 11, "bold") if is_selected else ("Arial", 11)
            cred_font = ("Consolas", 16, "bold") if is_selected else ("Consolas", 12, "bold")
            info['frame'].config(bg=bg_color)
            info['info_line'].config(bg=bg_color)
            info['cred_container'].config(bg=bg_color)
            info['char_label'].config(font=info_font, bg=bg_color, fg='#ffffff')
            info['server_label'].config(bg=bg_color)
            info['user_label'].config(font=cred_font, bg=bg_color, fg=fg_color)
            info['pass_label'].config(font=cred_font, bg=bg_color, fg=fg_color)
            if info['note_label']:
                note_fg_color = '#e0e0e0' if is_selected else '#aaaaaa'
                info['note_label'].config(bg=bg_color, fg=note_fg_color)

        char_name = character["name"]
        if char_name in self.recent_characters: self.recent_characters.remove(char_name)
        self.recent_characters.append(char_name)
        if len(self.recent_characters) > 3: self.recent_characters.pop(0)
        self.save_data()

    def add_character_dialog(self):
        dialog = tk.Toplevel(self.root); dialog.title("Add Character"); dialog.configure(bg='#2c2c2c')
        dialog.attributes("-topmost", True); dialog.transient(self.root); dialog.grab_set()
        dialog.geometry(f"350x480+{self.root.winfo_x()+50}+{self.root.winfo_y()+50}"); dialog.resizable(False, False)
        main_frame = tk.Frame(dialog, bg='#2c2c2c'); main_frame.pack(expand=True, fill='both', padx=15, pady=10)
        fields = ["Character Name", "Level", "Username", "Password", "Note (optional)"]; entries = {}
        for field in fields:
            f = tk.Frame(main_frame, bg='#2c2c2c'); f.pack(fill='x', pady=5)
            tk.Label(f, text=field + ":", bg='#2c2c2c', fg='white', font=("Arial", 10)).pack(side='left', anchor='w')
            entry = tk.Entry(f, font=("Arial", 10), bg="#555", fg="white", insertbackground="white", relief='solid', bd=1)
            entry.pack(side='right', expand=True, fill='x'); entries[field] = entry
        tk.Label(main_frame, text="Server:", bg='#2c2c2c', fg='white', font=("Arial", 10)).pack(pady=(10,2), anchor='w')
        server_var = tk.StringVar(); server_combo = ttk.Combobox(main_frame, textvariable=server_var, values=["Blue", "Green", "Red"], state="readonly")
        server_combo.pack(fill='x')
        tk.Label(main_frame, text="Class:", bg='#2c2c2c', fg='white', font=("Arial", 10)).pack(pady=(10,2), anchor='w')
        class_var = tk.StringVar(); class_combo = ttk.Combobox(main_frame, textvariable=class_var, values=self.eq_classes, state="readonly")
        class_combo.pack(fill='x')
        def add_character():
            if not all([entries["Character Name"].get(), entries["Level"].get(), server_var.get(), class_var.get(), entries["Username"].get(), entries["Password"].get()]):
                messagebox.showerror("Error", "Please fill in all required fields", parent=dialog); return
            try: level = int(entries["Level"].get())
            except ValueError: messagebox.showerror("Error", "Level must be a number", parent=dialog); return
            new_char = {"name": entries["Character Name"].get(), "level": level, "server": server_var.get(), "class": class_var.get(),
                        "username": entries["Username"].get(), "password": entries["Password"].get(), "note": entries["Note (optional)"].get()}
            self.accounts.append(new_char); self.refresh_character_list(); self.save_data(); dialog.destroy()
        btn_frame = tk.Frame(main_frame, bg='#2c2c2c'); btn_frame.pack(fill='x', pady=20)
        tk.Button(btn_frame, text="Add", command=add_character, bg='#0078D7', fg='white', font=("Arial", 10, "bold")).pack(side='left', expand=True, fill='x', padx=5, ipady=3)
        tk.Button(btn_frame, text="Cancel", command=dialog.destroy, bg='#555555', fg='white', font=("Arial", 10)).pack(side='right', expand=True, fill='x', padx=5, ipady=3)
        entries["Character Name"].focus()

    def on_exit(self):
        self.save_data()
        self.root.destroy()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    if platform.system() == "Windows":
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception as e:
            print(f"Could not set DPI awareness: {e}")
    app = actlist()
    app.run()