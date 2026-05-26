import tkinter as tk
from core.bundle_loader import BundleLoader
from core.monoscripts import MonoScriptManager
from core.ui.main_window import MainWindow


class DinoEditorApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Paleo Pines Dino Texture + Color Studio")

        self.bundle_loader = BundleLoader()
        self.monoscripts = MonoScriptManager(self.bundle_loader)

        self.window = MainWindow(self.root, self.bundle_loader, self.monoscripts)

    def run(self):
        self.root.geometry("1400x800")
        self.root.mainloop()
