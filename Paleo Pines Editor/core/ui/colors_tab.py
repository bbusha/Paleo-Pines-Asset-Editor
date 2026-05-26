import tkinter as tk
from tkinter import messagebox, colorchooser
from core.editors.color_editor import ColorEditor
from core.utils.color_utils import unity_color_to_rgb


class ColorsTab:
    def __init__(self, parent, bundle_loader, monoscripts):
        self.bundle_loader = bundle_loader
        self.monoscripts = monoscripts
        self.editor = ColorEditor(bundle_loader, monoscripts)

        self.frame = tk.Frame(parent)
        self.selected_color_index = None

        self.build_ui()

    def build_ui(self):
        body = tk.Frame(self.frame)
        body.pack(fill=tk.BOTH, expand=True)

        left = tk.Frame(body)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        tk.Label(left, text="MonoBehaviours (filtered):").pack(anchor="w")
        self.mb_listbox = tk.Listbox(left, width=50, height=25)
        self.mb_listbox.pack(fill=tk.Y, expand=True)
        self.mb_listbox.bind("<<ListboxSelect>>", self.on_select_mono)

        tk.Button(left, text="Rescan MonoBehaviours", command=self.refresh).pack(pady=4)

        right = tk.Frame(body)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        tk.Label(right, text="Color Fields:").pack(anchor="w")
        self.color_listbox = tk.Listbox(right, width=60, height=20)
        self.color_listbox.pack(fill=tk.BOTH, expand=True)
        self.color_listbox.bind("<<ListboxSelect>>", self.on_select_color_entry)

        btns = tk.Frame(right)
        btns.pack(fill=tk.X, pady=4)
        tk.Button(btns, text="Edit Selected Color", command=self.edit_selected_color).pack(side=tk.LEFT, padx=2)
        tk.Button(btns, text="Refresh Colors", command=self.refresh_color_entries).pack(side=tk.LEFT, padx=2)

    def refresh(self):
        self.mb_listbox.delete(0, tk.END)
        self.color_listbox.delete(0, tk.END)

        self.editor.scan_mono_behaviours()
        for obj, name, tree in self.editor.mono_behaviours:
            self.mb_listbox.insert(tk.END, name)

        self.refresh_color_entries()

    def refresh_color_entries(self):
        self.color_listbox.delete(0, tk.END)
        self.editor.build_color_entries()
        for line in self.editor.get_color_display_strings():
            self.color_listbox.insert(tk.END, line)

    def on_select_mono(self, event):
        pass

    def on_select_color_entry(self, event):
        if not self.color_listbox.curselection():
            self.selected_color_index = None
            return
        self.selected_color_index = self.color_listbox.curselection()[0]

    def edit_selected_color(self):
        if self.selected_color_index is None:
            messagebox.showerror("Error", "No color field selected.")
            return

        mb_index, path, color_dict = self.editor.color_entries[self.selected_color_index]
        r, g, b = unity_color_to_rgb(color_dict)

        new_color = colorchooser.askcolor(color=(r, g, b))
        if not new_color or not new_color[0]:
            return

        nr, ng, nb = map(int, new_color[0])
        self.editor.edit_color_entry(self.selected_color_index, (nr, ng, nb))
        self.refresh_color_entries()
