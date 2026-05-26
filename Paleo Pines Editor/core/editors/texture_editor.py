from PIL import Image, ImageChops


class TextureEditor:
    def __init__(self, dino_template_path="dino_template.png"):
        self.current_tex_obj = None
        self.current_tex_pil = None
        self.dino_template = None

        try:
            from PIL import Image as PILImage
            import os
            if os.path.isfile(dino_template_path):
                self.dino_template = PILImage.open(dino_template_path).convert("RGBA")
        except Exception:
            self.dino_template = None

    def set_texture_object(self, tex_obj):
        self.current_tex_obj = tex_obj
        if tex_obj is None:
            self.current_tex_pil = None
            return
        tex = tex_obj.read()
        img = tex.image
        self.current_tex_pil = img.convert("RGBA")

    def commit_to_env(self):
        if self.current_tex_obj is None or self.current_tex_pil is None:
            return
        tex = self.current_tex_obj.read()
        tex.set_image(self.current_tex_pil)
        tex.save()

    def paint_circle(self, x, y, radius, color):
        if self.current_tex_pil is None:
            return
        img = self.current_tex_pil
        pixels = img.load()
        r, g, b, a = color
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if dx * dx + dy * dy > radius * radius:
                    continue
                px = x + dx
                py = y + dy
                if 0 <= px < img.width and 0 <= py < img.height:
                    pixels[px, py] = (r, g, b, a)

    def get_dino_preview(self):
        if self.dino_template is None or self.current_tex_pil is None:
            return None
        tex = self.current_tex_pil.resize(self.dino_template.size, Image.NEAREST)
        base = self.dino_template.copy()
        white = Image.new("RGBA", base.size, (255, 255, 255, 255))
        tex_on_white = ImageChops.multiply(white, tex)
        r, g, b, a = base.split()
        composed = Image.composite(tex_on_white, base, a)
        return composed
