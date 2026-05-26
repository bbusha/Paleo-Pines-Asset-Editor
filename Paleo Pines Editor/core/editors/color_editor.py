from core.utils.search_utils import walk_typetree_for_colors
from core.utils.color_utils import unity_color_to_rgb, rgb_to_unity_color


class ColorEditor:
    def __init__(self, bundle_loader, monoscripts):
        self.bundle_loader = bundle_loader
        self.monoscripts = monoscripts

        self.mono_behaviours = []
        self.color_entries = []

    def scan_mono_behaviours(self):
        self.mono_behaviours.clear()

        env = self.bundle_loader.env
        if env is None:
            return

        for obj in env.objects:
            if obj.type.name == "MonoBehaviour":
                try:
                    name = getattr(obj.read(), "m_Name", None)
                    if not name:
                        name = f"(Mono_{obj.path_id})"

                    lname = name.lower()
                    if "color" in lname or "dino" in lname or "pattern" in lname:
                        tree = self.monoscripts.decode_mono(obj)
                        if tree:
                            self.mono_behaviours.append((obj, name, tree))

                except Exception as e:
                    print("Mono decode failed:", e)
                    continue

    def build_color_entries(self):
        self.color_entries.clear()

        for mb_index, (obj, name, tree) in enumerate(self.mono_behaviours):
            def on_color(path, color_dict):
                self.color_entries.append((mb_index, path, color_dict))

            walk_typetree_for_colors(tree, on_color)

    def get_color_display_strings(self):
        lines = []
        for mb_index, path, color_dict in self.color_entries:
            obj, name, tree = self.mono_behaviours[mb_index]
            r, g, b = unity_color_to_rgb(color_dict)
            a = color_dict.get("a", 1.0)
            lines.append(f"{name} :: {path} = ({r},{g},{b}, a={a:.2f})")
        return lines

    def edit_color_entry(self, index, new_rgb):
        mb_index, path, color_dict = self.color_entries[index]
        r, g, b = new_rgb

        rgb_to_unity_color(r, g, b, existing=color_dict)

        obj, name, tree = self.mono_behaviours[mb_index]

        # UnityPy 1.25+ save API
        obj.save_typetree(tree)
