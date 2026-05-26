import os
import UnityPy


class BundleLoader:
    def __init__(self):
        self.game_root = None
        self.bundle_paths = []
        self.current_bundle_path = None
        self.env = None

    def set_game_root(self, path: str):
        self.game_root = path
        self.scan_for_bundles()

    def scan_for_bundles(self):
        self.bundle_paths = []
        if not self.game_root or not os.path.isdir(self.game_root):
            return

        for root, dirs, files in os.walk(self.game_root):
            for f in files:
                if f.lower().endswith(".bundle"):
                    self.bundle_paths.append(os.path.join(root, f))

        self.bundle_paths.sort()

    def load_bundle(self, path: str):
        if not path or not os.path.isfile(path):
            return None
        self.current_bundle_path = path
        self.env = UnityPy.load(path)
        return self.env

    def save_bundle(self):
        if not self.env or not self.current_bundle_path:
            return None

        out_path = self.current_bundle_path.replace(".bundle", "_mod.bundle")
        data = self.env.file.save()
        with open(out_path, "wb") as f:
            f.write(data)
        return out_path
