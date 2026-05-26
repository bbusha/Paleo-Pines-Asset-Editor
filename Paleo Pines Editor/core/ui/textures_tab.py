import tkinter as tk
from tkinter import messagebox
from PIL import ImageTk
from core.editors.texture_editor import TextureEditor
from core.utils.texture_utils import resize_to_fit


class TexturesTab:
    def __init__(self, parent, bundle_loader):
        self.bundle_loader = bundle_loader
        self.editor = TextureEditor()

        self.frame = tk.Frame(parent)

        self.brush_color = (255, 0, 0, 255)
        self.brush_size = tk.IntVar(value=8)
        self.is_painting = False

        self.current_preview_imgtk = None
        self.current_dino_preview_imgtk = None

        self.build_ui()

    def build_ui(self):
        body = tk.Frame(self.frame)
        body.pack(fill=tk.BOTH, expand=True)

        left = tk.Frame(body)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        tk.Label(left, text="Textures in bundle:").pack(anchor="w")
        self.tex_listbox = tk.Listbox(left, width=40, height=30)
        self.tex_listbox.pack(fill=tk.Y, expand=True)
        self.tex_listbox.bind("<<ListboxSelect>>", self.on_select_texture)

        lf_btns = tk.Frame(left)
        lf_btns.pack(fill=tk.X, pady=4)
        tk.Button(lf_btns, text="Reload Bundle", command=self.reload_bundle).pack(side=tk.LEFT, padx=2)

        palette_frame = tk.LabelFrame(left, text="Palette")
        palette_frame.pack(fill=tk.X, pady=4)
        self.palette_list = tk.Listbox(palette_frame, height=6)
        self.palette_list.pack(fill=tk.X)
        pf_btns = tk.Frame(palette_frame)
        pf_btns.pack(fill=tk.X)
        tk.Button(pf_btns, text="Add Current", command=self.add_current_color_to_palette).pack(side=tk.LEFT, padx=2)
        tk.Button(pf_btns, text="Pick Color", command=self.pick_color_dialog).pack(side=tk.LEFT, padx=2)
        tk.Button(pf_btns, text="Use Selected", command=self.use_palette_color).pack(side=tk.LEFT, padx=2)

        brush_frame = tk.LabelFrame(left, text="Brush")
        brush_frame.pack(fill=tk.X, pady=4)
        tk.Label(brush_frame, text="Size").pack(side=tk.LEFT)
        tk.Scale(brush_frame, from_=1, to=64, orient=tk.HORIZONTAL,
                 variable=self.brush_size).pack(side=tk.LEFT, fill=tk.X, expand=True)

        right = tk.Frame(body)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        previews = tk.Frame(right)
        previews.pack(fill=tk.BOTH, expand=True)

        raw_frame = tk.LabelFrame(previews, text="Texture")
        raw_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)
        self.canvas = tk.Canvas(raw_frame, bg="gray")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<ButtonPress-1>", self.on_paint_start)
        self.canvas.bind("<B1-Motion>", self.on_paint_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_paint_end)
        self.canvas.bind("<ButtonPress-3>", self.on_pick_color)

        dino_frame = tk.LabelFrame(previews, text="Dino Preview")
        dino_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)
        self.dino_label = tk.Label(dino_frame, bg="black")
        self.dino_label.pack(fill=tk.BOTH, expand=True)

    def refresh(self):
        self.tex_listbox.delete(0, tk.END)
        self.editor.current_tex_obj = None
        self.editor.current_tex_pil = None
        self.canvas.delete("all")
        self.dino_label.config(image="", text="")

        env = self.bundle_loader.env
        if env is None:
            return

        self.textures = []
        for obj in env.objects:
            if obj.type.name == "Texture2D":
                tex = obj.read()
                name = getattr(tex, "m_Name", None)
                if not name or name.strip() == "":
                    name = f"(unnamed_{obj.path_id})"
                self.textures.append((obj, name))
                self.tex_listbox.insert(tk.END, name)

    def reload_bundle(self):
        if self.bundle_loader.current_bundle_path:
            self.bundle_loader.load_bundle(self.bundle_loader.current_bundle_path)
            self.refresh()

    def on_select_texture(self, event):
        if not self.tex_listbox.curselection():
            return
        idx = self.tex_listbox.curselection()[0]
        tex_obj, name = self.textures[idx]
        try:
            self.editor.set_texture_object(tex_obj)
            self.draw_texture_on_canvas()
            self.update_dino_preview()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read texture:\n{name}\n\n{e}")

    def canvas_to_image_coords(self, x, y):
        img = self.editor.current_tex_pil
        if img is None:
            return None, None
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        iw, ih = img.size
        scale = min(cw / iw, ch / ih)
        if scale <= 0:
            return None, None
        ox = (cw - iw * scale) / 2
        oy = (ch - ih * scale) / 2
        ix = int((x - ox) / scale)
        iy = int((y - oy) / scale)
        if 0 <= ix < iw and 0 <= iy < ih:
            return ix, iy
        return None, None

    def on_paint_start(self, event):
        if self.editor.current_tex_pil is None:
            return
        self.is_painting = True
        self.paint_at(event.x, event.y)

    def on_paint_move(self, event):
        if not self.is_painting or self.editor.current_tex_pil is None:
            return
        self.paint_at(event.x, event.y)

    def on_paint_end(self, event):
        self.is_painting = False
        self.editor.commit_to_env()

    def paint_at(self, x, y):
        ix, iy = self.canvas_to_image_coords(x, y)
        if ix is None:
            return
        self.editor.paint_circle(ix, iy, self.brush_size.get(), self.brush_color)
        self.draw_texture_on_canvas()
        self.update_dino_preview()

    def on_pick_color(self, event):
        img = self.editor.current_tex_pil
        if img is None:
            return
        ix, iy = self.canvas_to_image_coords(event.x, event.y)
        if ix is None:
            return
        r, g, b, a = img.getpixel((ix, iy))
        self.brush_color = (r, g, b, a)

    def draw_texture_on_canvas(self):
        img = self.editor.current_tex_pil
        if img is None:
            self.canvas.delete("all")
            return
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        if cw <= 1 or ch <= 1:
            self.frame.after(50, self.draw_texture_on_canvas)
            return
        resized = resize_to_fit(img, cw, ch)
        self.current_preview_imgtk = ImageTk.PhotoImage(resized)
        self.canvas.delete("all")
        self.canvas.create_image(cw // 2, ch // 2, image=self.current_preview_imgtk)

    def update_dino_preview(self):
        preview = self.editor.get_dino_preview()
        if preview is None:
            self.dino_label.config(image="", text="No dino template")
            return
        self.current_dino_preview_imgtk = ImageTk.PhotoImage(preview)
        self.dino_label.config(image=self.current_dino_preview_imgtk, text="")

    # palette

    def add_current_color_to_palette(self):
        r, g, b, a = self.brush_color
        entry = f"#{r:02X}{g:02X}{b:02X}"
        if entry not in self.palette_list.get(0, tk.END):
            self.palette_list.insert(tk.END, entry)

    def pick_color_dialog(self):
        from tkinter import colorchooser
        color = colorchooser.askcolor()
        if not color or not color[0]:
            return
        r, g, b = map(int, color[0])
        self.brush_color = (r, g, b, 255)

    def use_palette_color(self):
        if not self.palette_list.curselection():
            return
        idx = self.palette_list.curselection()[0]
        entry = self.palette_list.get(idx)
        r = int(entry[1:3], 16)
        g = int(entry[3:5], 16)
        b = int(entry[5:7], 16)
        self.brush_color = (r, g, b, 255)
