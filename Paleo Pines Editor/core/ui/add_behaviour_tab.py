import tkinter as tk
from tkinter import ttk, messagebox


class AddBehaviourTab:
    def __init__(self, parent, bundle_loader, monoscripts):
        self.bundle_loader = bundle_loader
        self.monoscripts = monoscripts

        self.frame = tk.Frame(parent)
        self.build_ui()

    def build_ui(self):
        body = tk.Frame(self.frame)
        body.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Script selector (informational for now)
        tk.Label(body, text="MonoScript Type:").grid(row=0, column=0, sticky="w")
        self.script_var = tk.StringVar()
        self.script_combo = ttk.Combobox(body, textvariable=self.script_var, width=40, state="readonly")
        self.script_combo.grid(row=0, column=1, sticky="w")

        # Name entry
        tk.Label(body, text="New Behaviour Name:").grid(row=1, column=0, sticky="w", pady=(10, 0))
        self.name_var = tk.StringVar()
        tk.Entry(body, textvariable=self.name_var, width=40).grid(row=1, column=1, sticky="w", pady=(10, 0))

        # Template selector
        tk.Label(body, text="Clone Existing Behaviour (required):").grid(row=2, column=0, sticky="w", pady=(10, 0))
        self.template_var = tk.StringVar()
        self.template_combo = ttk.Combobox(body, textvariable=self.template_var, width=40, state="readonly")
        self.template_combo.grid(row=2, column=1, sticky="w", pady=(10, 0))

        # Create button
        tk.Button(body, text="Clone Behaviour", command=self.create_behaviour).grid(
            row=3, column=0, columnspan=2, pady=20
        )

    def clone_behaviour_in_place(self, source_name, new_name):
        env = self.bundle_loader.env
        if env is None:
            raise Exception("No bundle loaded.")

        src_obj = None
        for obj in env.objects:
            if obj.type.name == "MonoBehaviour":
                mb = obj.read()
                if getattr(mb, "m_Name", "") == source_name:
                    src_obj = obj
                    break

        if not src_obj:
            raise Exception(f"Source behaviour '{source_name}' not found.")

        tree = src_obj.read_typetree()
        tree["m_Name"] = new_name

        src_obj.save_typetree(tree)
        return src_obj, tree

    def refresh(self):
        # Populate script list (informational)
        scripts = sorted(self.monoscripts.script_map.keys())
        self.script_combo["values"] = scripts

        # Populate template list
        env = self.bundle_loader.env
        templates = []
        if env:
            for obj in env.objects:
                if obj.type.name == "MonoBehaviour":
                    name = getattr(obj.read(), "m_Name", None)
                    if name:
                        templates.append(name)

        self.template_combo["values"] = sorted(templates)

    def create_behaviour(self):
        script_name = self.script_var.get().strip()
        new_name = self.name_var.get().strip()
        template_name = self.template_var.get().strip()

        if not script_name:
            messagebox.showerror("Error", "Select a MonoScript type (for reference).")
            return

        if not new_name:
            messagebox.showerror("Error", "Enter a name for the new behaviour.")
            return

        if not template_name:
            messagebox.showerror(
                "Error",
                "UnityPy cannot add brand-new behaviours.\n"
                "You must select an existing behaviour to clone."
            )
            return

        try:
            new_obj, tree = self.clone_behaviour_in_place(
                source_name=template_name,
                new_name=new_name
            )
            messagebox.showinfo("Success", f"Cloned behaviour:\n{template_name} → {new_name}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clone behaviour:\n{e}")
