import os
import UnityPy


class MonoScriptManager:
    def __init__(self, bundle_loader):
        self.bundle_loader = bundle_loader
        self.monoscripts_env = None
        self.script_map = {}

    def find_monoscripts(self):
        if not self.bundle_loader.game_root:
            return None

        for root, dirs, files in os.walk(self.bundle_loader.game_root):
            for f in files:
                if f.endswith("_monoscripts.bundle"):
                    return os.path.join(root, f)
        return None

    def load_monoscripts(self):
        path = self.find_monoscripts()
        if not path:
            print("No monoscripts bundle found.")
            return False

        print(f"Loading monoscripts: {path}")
        self.monoscripts_env = UnityPy.load(path)
        self.build_script_map()
        return True

    def build_script_map(self):
        self.script_map = {}

        if not self.monoscripts_env:
            print("No monoscripts env loaded.")
            return

        for obj in self.monoscripts_env.objects:
            if obj.type.name == "MonoScript":
                ms = obj.read()
                name = getattr(ms, "m_Name", None)
                if name:
                    self.script_map[name] = ms

        print(f"Loaded {len(self.script_map)} MonoScript definitions.")

    def decode_mono(self, obj):
        """
        UnityPy 1.25+ uses obj.read_typetree(), NOT mb.read_typetree().
        """
        try:
            return obj.read_typetree()
        except Exception as e:
            print("Typetree decode failed:", e)
            return None
