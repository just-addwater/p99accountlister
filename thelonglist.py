import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.font import Font
import json
import os
import platform

# A helper class to create simple tooltips that appear when hovering over a widget.
class ToolTip:
    """ Create a tooltip for a given widget. """
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.attributes("-topmost", True) # Ensure tooltip is on top
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(self.tooltip_window, text=self.text, justify='left',
                         background="#ffffe0", relief='solid', borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=2)

    def hide_tip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
        self.tooltip_window = None


class actlist:
    """ The main application class for the Account Lister. """
    def __init__(self):
        # --- Root Window Setup ---
        self.root = tk.Tk()
        self.root.title("Account Lister")
        self.root.attributes("-topmost", True)
        self.root.resizable(True, True)

        # --- Application State and Configuration ---
        self.alpha = 0.95
        self.window_position = {"x": 1000, "y": 100, "width": 420, "height": 700}
        self.accounts = []
        self.recent_characters = []
        self.favorites = []
        self.selected_server = "All"
        self.selected_character_data = None
        self.eq_classes = ["Bard", "Cleric", "Druid", "Enchanter", "Magician", "Monk", "Necromancer",
                         "Paladin", "Ranger", "Rogue", "Shadow Knight", "Shaman", "Warrior", "Wizard"]
        self.expanded_classes = {cls: True for cls in self.eq_classes}
        self.character_widgets = []
        self.class_header_widgets = {}
        self.last_viewed_class = None
        self.server_colors = {"Blue": "#4da6ff", "Green": "#4dff4d", "Red": "#ff4d4d", "All": "#ffffff"}

        # --- Style and Font Configuration ---
        self.root.configure(bg='#2c2c2c')
        style = ttk.Style(self.root)
        style.theme_use('clam')
     # This configures the default look of the Combobox
        style.configure("TCombobox", 
                        fieldbackground="#555", 
                        background="#555", 
                        foreground="white", 
                        selectbackground="#444",
                        arrowcolor="white")

        # This map specifically targets the 'readonly' state to ensure it also uses our dark theme.
        # This is the key fix for the white background issue.
        style.map("TCombobox",
                  fieldbackground=[('readonly', '#555')],
                  foreground=[('readonly', 'white')])
        style.configure("TScrollbar", background="#444", troughcolor="#2c2c2c", bordercolor="#2c2c2c", arrowcolor="white")
        
        # --- FIX for Combobox Dropdown Readability ---
        # This globally sets the style for the Listbox part of any TCombobox,
        # ensuring the dropdown menu is readable with our dark theme.
        self.root.option_add('*Listbox*Background', '#404040')
        self.root.option_add('*Listbox*Foreground', 'white')
        self.root.option_add('*Listbox*selectBackground', '#0078D7')
        self.root.option_add('*Listbox*selectForeground', 'white')

        self.fonts = {
            'char': Font(family="Arial", size=11),
            'char_bold': Font(family="Arial", size=11, weight='bold'),
            'note': Font(family="Arial", size=9, slant='italic'),
            'cred': Font(family="Consolas", size=12, weight='bold'),
            'cred_big': Font(family="Consolas", size=16, weight='bold')
        }

        # --- Initialization Sequence ---
        self.load_data()
        self.root.attributes("-alpha", self.alpha)
        self.setup_window()
        self.setup_ui()
        self.refresh_character_list()
        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)

    def setup_window(self):
        """Sets the initial size and position of the main window from loaded data."""
        width = self.window_position.get("width", 420)
        height = self.window_position.get("height", 700)
        x = self.window_position.get("x", 1000)
        y = self.window_position.get("y", 100)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.root.minsize(350, 700)

    def load_data(self):
        """Loads application state from the `act.txt` JSON file."""
        if os.path.exists("act.txt"):
            try:
                with open("act.txt", "r") as f:
                    data = json.load(f)
                    self.accounts = data.get("accounts", [])
                    self.recent_characters = data.get("recent", [])
                    self.favorites = data.get("favorites", [])
                    self.alpha = data.get("alpha", 0.95)
                    self.selected_server = data.get("last_server", "All")
                    self.window_position = data.get("window_position", self.window_position)
                    self.expanded_classes = data.get("expanded_classes", self.expanded_classes)
            except (json.JSONDecodeError, FileNotFoundError):
                self.create_default_file()
        else:
            self.create_default_file()

    def create_default_file(self):
        """Creates a default `act.txt` file if one doesn't exist or is corrupted."""
        default_data = {
            "accounts": [], "recent": [], "favorites": [], "last_server": "All",
            "window_position": self.window_position,
            "expanded_classes": self.expanded_classes,
            "alpha": self.alpha
        }
        with open("act.txt", "w") as f:
            json.dump(default_data, f, indent=4)
        self.accounts, self.recent_characters, self.favorites = [], [], []

    def save_data(self):
        """Saves the current application state to `act.txt`."""
        data = {
            "accounts": self.accounts,
            "recent": self.recent_characters[-3:],
            "favorites": self.favorites,
            "last_server": self.selected_server,
            "window_position": {
                "x": self.root.winfo_x(), "y": self.root.winfo_y(),
                "width": self.root.winfo_width(), "height": self.root.winfo_height()
            },
            "expanded_classes": self.expanded_classes,
            "alpha": self.alpha
        }
        with open("act.txt", "w") as f:
            json.dump(data, f, indent=4)

    def setup_ui(self):
        """Creates and arranges the main UI components."""
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
        button_frame.grid_columnconfigure(0, weight=2)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_columnconfigure(2, weight=1)

        add_btn = tk.Button(button_frame, text="Add Character", command=self.add_character_dialog,
                             bg='#0078D7', fg='white', font=("Arial", 10, "bold"), relief='raised', bd=2)
        add_btn.grid(row=0, column=0, sticky='ew', padx=(0, 5))

        # Changed button color to match Exit button
        edit_btn = tk.Button(button_frame, text="Edit Character", command=self.edit_character_dialog,
                              bg='#555555', fg='white', font=("Arial", 10, "bold"), relief='raised', bd=2)
        edit_btn.grid(row=0, column=1, sticky='ew', padx=5)

        exit_btn = tk.Button(button_frame, text="Exit", command=self.on_exit,
                              bg='#555555', fg='white', font=("Arial", 10), relief='raised', bd=2)
        exit_btn.grid(row=0, column=2, sticky='ew', padx=(5, 0))

    def setup_scrollable_frame(self):
        """Sets up the scrollable area using a Canvas widget."""
        canvas_frame = tk.Frame(self.root, bg='#2c2c2c')
        canvas_frame.pack(fill='both', expand=True, padx=10, pady=5)
        self.canvas = tk.Canvas(canvas_frame, bg='#2c2c2c', highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg='#2c2c2c')
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.root.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)
        self.update_text_truncation()

    def _on_mousewheel(self, event):
        if platform.system() == "Windows":
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        else:
            if event.num == 5: self.canvas.yview_scroll(1, "units")
            elif event.num == 4: self.canvas.yview_scroll(-1, "units")

    def on_server_change(self):
        self.capture_current_view_class()
        self.selected_server = self.server_var.get()
        self.refresh_character_list()

    def refresh_character_list(self):
        self.canvas.yview_moveto(0)
        for widget in self.scrollable_frame.winfo_children(): widget.destroy()
        self.character_widgets.clear()
        self.class_header_widgets.clear()
        
        filtered_accounts = [acc for acc in self.accounts if self.selected_server == "All" or acc["server"] == self.selected_server]
        
        recent_chars_data = [next((acc for acc in self.accounts if acc["name"] == name), None) for name in reversed(self.recent_characters)]
        recent_chars_data = [char for char in recent_chars_data if char and (self.selected_server == "All" or char["server"] == self.selected_server)]
        if recent_chars_data:
            tk.Label(self.scrollable_frame, text="Recent", font=("Arial", 14, "bold"), bg='#2c2c2c', fg='#ffff4d').pack(anchor='w', pady=(0, 8))
            for char_data in recent_chars_data: self.create_character_widget(char_data, is_recent=True)

        fav_chars_data = [next((acc for acc in self.accounts if acc["name"] == name), None) for name in sorted(self.favorites)]
        fav_chars_data = [char for char in fav_chars_data if char and (self.selected_server == "All" or char["server"] == self.selected_server)]
        if fav_chars_data:
            tk.Label(self.scrollable_frame, text="Favorites", font=("Arial", 14, "bold"), bg='#2c2c2c', fg='#ffd700').pack(anchor='w', pady=(10, 8))
            for char_data in fav_chars_data: self.create_character_widget(char_data, is_recent=True)

        class_groups = {cls: [] for cls in self.eq_classes}
        for account in filtered_accounts: class_groups[account["class"]].append(account)

        for eq_class in self.eq_classes:
            characters = class_groups[eq_class]
            header_frame = tk.Frame(self.scrollable_frame, bg='#2c2c2c')
            header_frame.pack(fill='x', pady=(10, 2))
            is_expanded = self.expanded_classes.get(eq_class, True)
            arrow, fg_color = ("▼", '#ffffff') if is_expanded else ("▶", '#ffffff')
            if not characters: fg_color = '#666666'
            class_text = f"{arrow} {eq_class} ({len(characters)})"
            class_label = tk.Label(header_frame, text=class_text, font=("Arial", 12, "bold"), bg='#2c2c2c', fg=fg_color, cursor="hand2")
            class_label.pack(anchor='w')
            class_label.bind("<Button-1>", lambda e, cls=eq_class: self.toggle_class_expansion(cls))
            self.class_header_widgets[eq_class] = header_frame
            if is_expanded:
                for character in sorted(characters, key=lambda c: c['name']): self.create_character_widget(character)
        
        self.autosize_window_width(filtered_accounts)
        self.root.update_idletasks()
        self.restore_class_view()
        self.update_text_truncation()

    def update_text_truncation(self):
        for info in self.character_widgets:
            char_width = info['info_line'].winfo_width() - info['right_panel'].winfo_width() - 20
            self._truncate_text(info['char_label'], info['full_text_char'], char_width, info['font_char'])
            if info['note_label']:
                note_width = info['frame'].winfo_width() - 20
                self._truncate_text(info['note_label'], info['full_text_note'], note_width, self.fonts['note'])
            cred_width = info['cred_container'].winfo_width() - 10
            self._truncate_text(info['user_label'], info['full_text_user'], cred_width, info['font_cred'])
            self._truncate_text(info['pass_label'], info['full_text_pass'], cred_width, info['font_cred'])
            
    def _truncate_text(self, label, full_text, max_width, font):
        if max_width < 20: return
        if font.measure(full_text) <= max_width: label.config(text=full_text)
        else:
            for i in range(len(full_text) - 1, 0, -1):
                if font.measure(full_text[:i] + "...") <= max_width:
                    label.config(text=full_text[:i] + "...")
                    return
            label.config(text="...")

    def capture_current_view_class(self):
        self.last_viewed_class = None
        self.root.update_idletasks()
        try:
            scroll_region_height = self.canvas.bbox("all")[3]
            if scroll_region_height == 0: return
            view_top_y = self.canvas.yview()[0] * scroll_region_height
            top_class = None
            for class_name, header_widget in self.class_header_widgets.items():
                if header_widget.winfo_y() <= view_top_y: top_class = class_name
            self.last_viewed_class = top_class
        except (TypeError, IndexError): self.last_viewed_class = None

    def restore_class_view(self):
        if self.last_viewed_class and self.last_viewed_class in self.class_header_widgets:
            target_widget = self.class_header_widgets[self.last_viewed_class]
            try:
                total_height = self.canvas.bbox("all")[3]
                if total_height > 0:
                    self.canvas.yview_moveto(target_widget.winfo_y() / total_height)
            except (TypeError, IndexError): self.canvas.yview_moveto(0)
        else: self.canvas.yview_moveto(0)
        self.last_viewed_class = None

    def create_character_widget(self, character, is_recent=False):
        char_frame = tk.Frame(self.scrollable_frame, bg='#404040', relief='solid', bd=1)
        char_frame.pack(fill='x', padx=5, pady=3)
        info_line = tk.Frame(char_frame, bg='#404040')
        info_line.pack(fill='x', padx=8, pady=(5,0))
        info_line.grid_columnconfigure(0, weight=1); info_line.grid_columnconfigure(1, weight=0)
        full_text_char = f"{character['name']} - {character['class']} (Lvl {character['level']})" if is_recent else f"{character['name']} (Lvl {character['level']})"
        char_label = tk.Label(info_line, text=full_text_char, font=self.fonts['char'], bg='#404040', fg='white', anchor='w')
        char_label.grid(row=0, column=0, sticky='ew')
        right_panel = tk.Frame(info_line, bg='#404040')
        right_panel.grid(row=0, column=1, sticky='e', padx=(10, 0))
        server_label = tk.Label(right_panel, text=character["server"], font=("Arial", 10, "bold"), bg='#404040', fg=self.server_colors[character["server"]], anchor='e')
        server_label.pack(anchor='e')
        is_fav = character['name'] in self.favorites
        star_char, star_color = ("★", "#ffd700") if is_fav else ("☆", "#999999")
        star_label = tk.Label(right_panel, text=star_char, font=("Arial", 12), bg='#404040', fg=star_color, cursor="hand2")
        star_label.pack(anchor='e', pady=(2, 0))
        star_label.bind("<Button-1>", lambda e, char_name=character['name']: self.toggle_favorite(char_name))
        ToolTip(star_label, "Remove from favorites" if is_fav else "Add to favorites")
        note_label = None; full_text_note = character.get("note", "")
        if full_text_note:
            note_label = tk.Label(char_frame, text=full_text_note, font=self.fonts['note'], bg='#404040', fg='#ccc', anchor='w')
            note_label.pack(fill='x', padx=8)
        cred_container = tk.Frame(char_frame, bg='#404040', height=65)
        cred_container.pack(fill='x', padx=8, pady=(5,5)); cred_container.pack_propagate(False)
        full_text_user = f"User: {character['username']}"; full_text_pass = f"Pass: {character['password']}"
        username_label = tk.Label(cred_container, text=full_text_user, font=self.fonts['cred'], bg='#404040', fg='white', anchor='w')
        username_label.pack(fill='x')
        password_label = tk.Label(cred_container, text=full_text_pass, font=self.fonts['cred'], bg='#404040', fg='white', anchor='w')
        password_label.pack(fill='x')
        widget_info = {'frame': char_frame, 'info_line': info_line, 'right_panel': right_panel, 'char_label': char_label, 'server_label': server_label, 'star_label': star_label, 'cred_container': cred_container, 'user_label': username_label, 'pass_label': password_label, 'note_label': note_label, 'full_text_char': full_text_char, 'full_text_note': full_text_note, 'full_text_user': full_text_user, 'full_text_pass': full_text_pass, 'font_char': self.fonts['char'], 'font_cred': self.fonts['cred']}
        self.character_widgets.append(widget_info)
        def on_click(event): self.on_character_click(character, widget_info)
        for widget in [char_frame, info_line, char_label, server_label, cred_container, username_label, password_label, right_panel]:
            widget.bind("<Button-1>", on_click); widget.configure(cursor="hand2")
        if note_label: note_label.bind("<Button-1>", on_click); note_label.configure(cursor="hand2")

    def on_character_click(self, character, clicked_widget_info):
        self.selected_character_data = character
        for info in self.character_widgets:
            is_selected = (info == clicked_widget_info)
            bg_color = '#005a9e' if is_selected else '#404040'
            info['font_char'] = self.fonts['char_bold'] if is_selected else self.fonts['char']
            info['font_cred'] = self.fonts['cred_big'] if is_selected else self.fonts['cred']
            info['frame'].config(bg=bg_color); info['info_line'].config(bg=bg_color); info['cred_container'].config(bg=bg_color); info['right_panel'].config(bg=bg_color); info['server_label'].config(bg=bg_color); info['star_label'].config(bg=bg_color)
            info['char_label'].config(font=info['font_char'], bg=bg_color, fg='#ffffff')
            info['user_label'].config(font=info['font_cred'], bg=bg_color, fg=('#ffffff' if is_selected else '#aaaaaa'))
            info['pass_label'].config(font=info['font_cred'], bg=bg_color, fg=('#ffffff' if is_selected else '#aaaaaa'))
            if info['note_label']: info['note_label'].config(bg=bg_color, fg=('#e0e0e0' if is_selected else '#aaaaaa'))
        self.update_text_truncation()
        char_name = character["name"]
        if char_name in self.recent_characters: self.recent_characters.remove(char_name)
        self.recent_characters.append(char_name)
        if len(self.recent_characters) > 3: self.recent_characters.pop(0)
        self.save_data()
    
    def edit_character_dialog(self):
        if not self.selected_character_data: return
        dialog = tk.Toplevel(self.root); dialog.title("Edit Character"); dialog.configure(bg='#2c2c2c'); dialog.attributes("-topmost", True); dialog.transient(self.root); dialog.grab_set(); dialog.geometry(f"350x520+{self.root.winfo_x()+50}+{self.root.winfo_y()+50}"); dialog.resizable(False, False)
        main_frame = tk.Frame(dialog, bg='#2c2c2c'); main_frame.pack(expand=True, fill='both', padx=15, pady=10)
        field_map = {"Character Name": "name", "Level": "level", "Username": "username", "Password": "password", "Note (optional)": "note"}
        entries = {}
        for field_text, data_key in field_map.items():
            f = tk.Frame(main_frame, bg='#2c2c2c'); f.pack(fill='x', pady=5)
            tk.Label(f, text=field_text + ":", bg='#2c2c2c', fg='white', font=("Arial", 10)).pack(side='left', anchor='w')
            entry = tk.Entry(f, font=("Arial", 10), bg="#555", fg="white", insertbackground="white", relief='solid', bd=1)
            entry.insert(0, self.selected_character_data.get(data_key, "")); entry.pack(side='right', expand=True, fill='x'); entries[field_text] = entry
        tk.Label(main_frame, text="Server:", bg='#2c2c2c', fg='white', font=("Arial", 10)).pack(pady=(10,2), anchor='w')
        server_var = tk.StringVar(value=self.selected_character_data.get("server")); server_combo = ttk.Combobox(main_frame, textvariable=server_var, values=["Blue", "Green", "Red"], state="readonly"); server_combo.pack(fill='x')
        tk.Label(main_frame, text="Class:", bg='#2c2c2c', fg='white', font=("Arial", 10)).pack(pady=(10,2), anchor='w')
        class_var = tk.StringVar(value=self.selected_character_data.get("class")); class_combo = ttk.Combobox(main_frame, textvariable=class_var, values=self.eq_classes, state="readonly"); class_combo.pack(fill='x')
        
        def save_character():
            if not all([entries["Character Name"].get(), entries["Level"].get(), server_var.get(), class_var.get(), entries["Username"].get(), entries["Password"].get()]):
                messagebox.showerror("Error", "Please fill in all required fields", parent=dialog); return
            try: level = int(entries["Level"].get())
            except ValueError: messagebox.showerror("Error", "Level must be a number", parent=dialog); return
            
            scroll_pos = self.canvas.yview()[0] # Capture scroll pos before refresh
            
            self.selected_character_data['name'] = entries["Character Name"].get()
            self.selected_character_data['level'] = level
            self.selected_character_data['server'] = server_var.get()
            self.selected_character_data['class'] = class_var.get()
            self.selected_character_data['username'] = entries["Username"].get()
            self.selected_character_data['password'] = entries["Password"].get()
            self.selected_character_data['note'] = entries["Note (optional)"].get()
            
            self.save_data()
            self.refresh_character_list()
            self.root.update_idletasks() # Ensure list is redrawn
            self.canvas.yview_moveto(scroll_pos) # Restore scroll pos
            dialog.destroy()

        def delete_character():
            char_name = self.selected_character_data['name']
            if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to permanently delete {char_name}?", parent=dialog):
                return
            
            scroll_pos = self.canvas.yview()[0] # Capture scroll pos
            
            # Remove from all relevant lists
            self.accounts.remove(self.selected_character_data)
            if char_name in self.favorites: self.favorites.remove(char_name)
            if char_name in self.recent_characters: self.recent_characters.remove(char_name)
            
            self.selected_character_data = None # Deselect
            self.save_data()
            self.refresh_character_list()
            self.root.update_idletasks()
            self.canvas.yview_moveto(scroll_pos) # Restore scroll pos
            dialog.destroy()

        btn_frame = tk.Frame(main_frame, bg='#2c2c2c'); btn_frame.pack(fill='x', pady=20)
        tk.Button(btn_frame, text="Save", command=save_character, bg='#0078D7', fg='white', font=("Arial", 10, "bold")).pack(side='left', expand=True, fill='x', padx=5, ipady=3)
        tk.Button(btn_frame, text="Cancel", command=dialog.destroy, bg='#555555', fg='white', font=("Arial", 10)).pack(side='right', expand=True, fill='x', padx=5, ipady=3)
        
        # Delete button at the very bottom
        delete_btn = tk.Button(main_frame, text="Delete Character", command=delete_character, bg='#c0392b', fg='white', font=("Arial", 10, "bold"))
        delete_btn.pack(fill='x', pady=(10, 0), ipady=3)
        
        entries["Character Name"].focus()

    def toggle_class_expansion(self, eq_class):
        self.expanded_classes[eq_class] = not self.expanded_classes.get(eq_class, True)
        self.refresh_character_list()

    def toggle_favorite(self, character_name):
        scroll_pos = self.canvas.yview()[0]
        if character_name in self.favorites: self.favorites.remove(character_name)
        else: self.favorites.append(character_name)
        self.save_data(); self.refresh_character_list(); self.root.update_idletasks(); self.canvas.yview_moveto(scroll_pos)

    def autosize_window_width(self, accounts):
        if not accounts: return
        max_pixel_width = 0
        for acc in accounts:
            width = self.fonts['char_bold'].measure(f"{acc['name']} (Lvl {acc['level']})")
            if width > max_pixel_width: max_pixel_width = width
        required_width = max_pixel_width + 160
        capped_width = min(required_width, 600)
        if capped_width > self.root.winfo_width(): self.root.geometry(f"{capped_width}x{self.root.winfo_height()}")

    def add_character_dialog(self):
        dialog = tk.Toplevel(self.root); dialog.title("Add Character"); dialog.configure(bg='#2c2c2c'); dialog.attributes("-topmost", True); dialog.transient(self.root); dialog.grab_set(); dialog.geometry(f"350x480+{self.root.winfo_x()+50}+{self.root.winfo_y()+50}"); dialog.resizable(False, False)
        main_frame = tk.Frame(dialog, bg='#2c2c2c'); main_frame.pack(expand=True, fill='both', padx=15, pady=10)
        fields = ["Character Name", "Level", "Username", "Password", "Note (optional)"]; entries = {}
        for field in fields:
            f = tk.Frame(main_frame, bg='#2c2c2c'); f.pack(fill='x', pady=5)
            tk.Label(f, text=field + ":", bg='#2c2c2c', fg='white', font=("Arial", 10)).pack(side='left', anchor='w')
            entry = tk.Entry(f, font=("Arial", 10), bg="#555", fg="white", insertbackground="white", relief='solid', bd=1); entry.pack(side='right', expand=True, fill='x'); entries[field] = entry
        tk.Label(main_frame, text="Server:", bg='#2c2c2c', fg='white', font=("Arial", 10)).pack(pady=(10,2), anchor='w')
        server_var = tk.StringVar(); server_combo = ttk.Combobox(main_frame, textvariable=server_var, values=["Blue", "Green", "Red"], state="readonly"); server_combo.pack(fill='x')
        tk.Label(main_frame, text="Class:", bg='#2c2c2c', fg='white', font=("Arial", 10)).pack(pady=(10,2), anchor='w')
        class_var = tk.StringVar(); class_combo = ttk.Combobox(main_frame, textvariable=class_var, values=self.eq_classes, state="readonly"); class_combo.pack(fill='x')
        def add_character():
            if not all([entries["Character Name"].get(), entries["Level"].get(), server_var.get(), class_var.get(), entries["Username"].get(), entries["Password"].get()]):
                messagebox.showerror("Error", "Please fill in all required fields", parent=dialog); return
            try: level = int(entries["Level"].get())
            except ValueError: messagebox.showerror("Error", "Level must be a number", parent=dialog); return
            new_char = {"name": entries["Character Name"].get(), "level": level, "server": server_var.get(), "class": class_var.get(), "username": entries["Username"].get(), "password": entries["Password"].get(), "note": entries["Note (optional)"].get()}
            self.accounts.append(new_char); self.save_data(); self.refresh_character_list(); dialog.destroy()
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
