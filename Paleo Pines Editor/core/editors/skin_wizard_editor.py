from PIL import Image, ImageChops
import copy


class SkinWizardEditor:
    def __init__(self, bundle_loader, monoscripts, texture_editor):
        self.bundle_loader = bundle_loader
        self.monoscripts = monoscripts
        self.texture_editor = texture_editor

    def get_species_list(self):
        env = self.bundle_loader.env
        species = []
        for obj in env.objects:
            if obj.type.name == "MonoBehaviour":
                mb = obj.read()
                name = getattr(mb, "m_Name", "")
                if "Species" in name:
                    species.append(name)
        return sorted(species)

    def get_pattern_list(self):
        env = self.bundle_loader.env
        patterns = []
        for obj in env.objects:
            if obj.type.name == "Texture2D":
                tex = obj.read()
                name = getattr(tex, "m_Name", "")
                if "pattern" in name.lower():
                    patterns.append(name)
        return sorted(patterns)

    def get_existing_skins(self):
        env = self.bundle_loader.env
        skins = []
        for obj in env.objects:
            if obj.type.name == "MonoBehaviour":
                mb = obj.read()
                name = getattr(mb, "m_Name", "")
                if "Skin" in name or "Color" in name:
                    skins.append(name)
        return sorted(skins)

    def generate_preview(self, primary, secondary, pattern_color):
        if not self.texture_editor.dino_template:
            return None

        base = self.texture_editor.dino_template.copy()

        # Fake preview: multiply colors onto template
        color_layer = Image.new("RGBA", base.size, primary + (255,))
        preview = ImageChops.multiply(base, color_layer)

        return preview

    def create_skin(self, species, pattern, primary, secondary, pattern_color, clone_name):
        env = self.bundle_loader.env

        # Find script
        if "DinoColor" not in self.monoscripts.script_map:
            raise Exception("DinoColor script not found.")

        script_obj = self.monoscripts.script_map["DinoColor"]

        # Clone or create new typetree
        if clone_name:
            template_tree = None
            for obj in env.objects:
                if obj.type.name == "MonoBehaviour":
                    mb = obj.read()
                    if getattr(mb, "m_Name", "") == clone_name:
                        template_tree = obj.read_typetree()
                        break
            if not template_tree:
                raise Exception("Clone source not found.")
            tree = copy.deepcopy(template_tree)
        else:
            tree = {
                "m_Name": f"CustomSkin_{species}",
                "m_Script": {
                    "m_FileID": script_obj.m_FileID,
                    "m_PathID": script_obj.m_PathID,
                },
                "primaryColor": {"r": primary[0]/255, "g": primary[1]/255, "b": primary[2]/255, "a": 1},
                "secondaryColor": {"r": secondary[0]/255, "g": secondary[1]/255, "b": secondary[2]/255, "a": 1},
                "patternColor": {"r": pattern_color[0]/255, "g": pattern_color[1]/255, "b": pattern_color[2]/255, "a": 1},
                "patternName": pattern,
                "speciesName": species,
            }

        # Create new MonoBehaviour
        new_obj = env.add_object(114)
        new_obj.save_typetree(tree)

        return new_obj
