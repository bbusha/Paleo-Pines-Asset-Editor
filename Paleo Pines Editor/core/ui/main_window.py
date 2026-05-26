import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from core.ui.textures_tab import TexturesTab
from core.ui.colors_tab import ColorsTab
from core.ui.add_behaviour_tab import AddBehaviourTab


class MainWindow:
    def __init__(self, root, bundle_loader, monoscripts):
        self.root = root
        self.bundle_loader = bundle_loader
        self.monoscripts = monoscripts

        self.build_ui()

    def build_ui(self):
        top = tk.Frame(self.root)
        top.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(top, text="Game Root:").pack(side=tk.LEFT)
        self.game_root_var = tk.StringVar()
        tk.Entry(top, textvariable=self.game_root_var, width=60).pack(side=tk.LEFT, padx=4)
        tk.Button(top, text="Browse...", command=self.browse_root).pack(side=tk.LEFT, padx=2)
        tk.Button(top, text="Rescan Bundles", command=self.rescan).pack(side=tk.LEFT, padx=2)

        tk.Label(top, text="Bundle:").pack(side=tk.LEFT, padx=(10, 2))
        self.bundle_var = tk.StringVar()
        self.bundle_combo = ttk.Combobox(top, textvariable=self.bundle_var, width=60, state="readonly")
        self.bundle_combo.pack(side=tk.LEFT, padx=4)
        self.bundle_combo.bind("<<ComboboxSelected>>", self.on_bundle_selected)

        tk.Button(top, text="Save Modded Bundle", command=self.save_bundle).pack(side=tk.LEFT, padx=4)

        # Notebook must be created BEFORE adding tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.textures_tab = TexturesTab(notebook, self.bundle_loader)
        self.colors_tab = ColorsTab(notebook, self.bundle_loader, self.monoscripts)
        self.add_behaviour_tab = AddBehaviourTab(notebook, self.bundle_loader, self.monoscripts)

        notebook.add(self.textures_tab.frame, text="Textures")
        notebook.add(self.colors_tab.frame, text="Color Behaviours")
        notebook.add(self.add_behaviour_tab.frame, text="Add Behaviour")

    def browse_root(self):
        path = filedialog.askdirectory()
        if not path:
            return

        self.game_root_var.set(path)
        self.bundle_loader.set_game_root(path)

        # Load monoscripts BEFORE scanning bundles
        if not self.monoscripts.load_monoscripts():
            messagebox.showerror("Error", "Could not load monoscripts bundle.")
            return

        self.update_bundle_dropdown()

    def rescan(self):
        root = self.game_root_var.get().strip()
        if not root:
            messagebox.showerror("Error", "Please select a game root first.")
            return

        self.bundle_loader.set_game_root(root)
        self.update_bundle_dropdown()

    def update_bundle_dropdown(self):
        names = [os.path.basename(p) for p in self.bundle_loader.bundle_paths]
        self.bundle_combo["values"] = names

        if names:
            self.bundle_combo.current(0)
            self.on_bundle_selected(None)

    def on_bundle_selected(self, event):
        idx = self.bundle_combo.current()
        if idx < 0 or idx >= len(self.bundle_loader.bundle_paths):
            return

        path = self.bundle_loader.bundle_paths[idx]
        self.bundle_loader.load_bundle(path)

        # Refresh all tabs
        self.textures_tab.refresh()
        self.colors_tab.refresh()
        self.add_behaviour_tab.refresh()

    def save_bundle(self):
        out = self.bundle_loader.save_bundle()
        if out:
            messagebox.showinfo("Saved", f"Modded bundle saved as:\n{out}")
        else:
            messagebox.showerror("Error", "No bundle loaded to save.")
