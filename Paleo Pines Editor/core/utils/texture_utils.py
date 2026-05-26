from PIL import Image


def resize_to_fit(img: Image.Image, max_w: int, max_h: int) -> Image.Image:
    if img is None:
        return None
    iw, ih = img.size
    if iw == 0 or ih == 0:
        return img
    scale = min(max_w / iw, max_h / ih)
    if scale <= 0:
        return img
    return img.resize((int(iw * scale), int(ih * scale)), Image.NEAREST)
