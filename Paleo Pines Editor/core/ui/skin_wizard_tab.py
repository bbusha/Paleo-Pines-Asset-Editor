import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
from PIL import ImageTk
from core.editors.skin_wizard_editor import SkinWizardEditor


class SkinWizardTab:
    def __init__(self, parent, bundle_loader, monoscripts, texture_editor):
        self.bundle_loader = bundle_loader
        self.monoscripts = monoscripts
        self.texture_editor = texture_editor
        self.editor = SkinWizardEditor(bundle_loader, monoscripts, texture_editor)

        self.frame = tk.Frame(parent)

        self.primary_color = (255, 255, 255)
        self.secondary_color = (255, 255, 255)
        self.pattern_color = (255, 255, 255)

        self.preview_imgtk = None

        self.build_ui()

    def build_ui(self):
        body = tk.Frame(self.frame)
        body.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Species
        tk.Label(body, text="Species:").grid(row=0, column=0, sticky="w")
        self.species_var = tk.StringVar()
        self.species_combo = ttk.Combobox(body, textvariable=self.species_var, width=40, state="readonly")
        self.species_combo.grid(row=0, column=1, sticky="w")

        # Pattern
        tk.Label(body, text="Pattern:").grid(row=1, column=0, sticky="w", pady=(10, 0))
        self.pattern_var = tk.StringVar()
        self.pattern_combo = ttk.Combobox(body, textvariable=self.pattern_var, width=40, state="readonly")
        self.pattern_combo.grid(row=1, column=1, sticky="w", pady=(10, 0))

        # Colors
        tk.Label(body, text="Primary Color:").grid(row=2, column=0, sticky="w", pady=(10, 0))
        tk.Button(body, text="Pick", command=self.pick_primary).grid(row=2, column=1, sticky="w")

        tk.Label(body, text="Secondary Color:").grid(row=3, column=0, sticky="w", pady=(10, 0))
        tk.Button(body, text="Pick", command=self.pick_secondary).grid(row=3, column=1, sticky="w")

        tk.Label(body, text="Pattern Color:").grid(row=4, column=0, sticky="w", pady=(10, 0))
        tk.Button(body, text="Pick", command=self.pick_pattern_color).grid(row=4, column=1, sticky="w")

        # Preview
        preview_frame = tk.LabelFrame(body, text="Preview")
        preview_frame.grid(row=0, column=2, rowspan=6, padx=20)
        self.preview_label = tk.Label(preview_frame, bg="black")
        self.preview_label.pack(fill=tk.BOTH, expand=True)

        # Clone
        tk.Label(body, text="Clone Existing Skin (optional):").grid(row=5, column=0, sticky="w", pady=(10, 0))
        self.clone_var = tk.StringVar()
        self.clone_combo = ttk.Combobox(body, textvariable=self.clone_var, width=40, state="readonly")
        self.clone_combo.grid(row=5, column=1, sticky="w", pady=(10, 0))

        # Create button
        tk.Button(body, text="Generate Skin", command=self.generate_skin).grid(
            row=6, column=0, columnspan=2, pady=20
        )

    def refresh(self):
        # Populate species list
        species = self.editor.get_species_list()
        self.species_combo["values"] = species

        # Populate patterns
        patterns = self.editor.get_pattern_list()
        self.pattern_combo["values"] = patterns

        # Populate clone list
        clones = self.editor.get_existing_skins()
        self.clone_combo["values"] = clones

    def pick_primary(self):
        c = colorchooser.askcolor()
        if c[0]:
            self.primary_color = tuple(map(int, c[0]))
            self.update_preview()

    def pick_secondary(self):
        c = colorchooser.askcolor()
        if c[0]:
            self.secondary_color = tuple(map(int, c[0]))
            self.update_preview()

    def pick_pattern_color(self):
        c = colorchooser.askcolor()
        if c[0]:
            self.pattern_color = tuple(map(int, c[0]))
            self.update_preview()

    def update_preview(self):
        img = self.editor.generate_preview(
            self.primary_color,
            self.secondary_color,
            self.pattern_color
        )
        if img:
            self.preview_imgtk = ImageTk.PhotoImage(img)
            self.preview_label.config(image=self.preview_imgtk)

    def generate_skin(self):
        species = self.species_var.get()
        pattern = self.pattern_var.get()
        clone = self.clone_var.get()

        if not species:
            messagebox.showerror("Error", "Select a species.")
            return

        if not pattern:
            messagebox.showerror("Error", "Select a pattern.")
            return

        try:
            self.editor.create_skin(
                species,
                pattern,
                self.primary_color,
                self.secondary_color,
                self.pattern_color,
                clone
            )
            messagebox.showinfo("Success", "Custom skin created successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create skin:\n{e}")
