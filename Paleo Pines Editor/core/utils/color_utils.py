def unity_color_to_rgb(color_dict):
    r = float(color_dict.get("r", 0.0))
    g = float(color_dict.get("g", 0.0))
    b = float(color_dict.get("b", 0.0))
    return int(r * 255), int(g * 255), int(b * 255)


def rgb_to_unity_color(r, g, b, a=None, existing=None):
    d = existing if isinstance(existing, dict) else {}
    d["r"] = r / 255.0
    d["g"] = g / 255.0
    d["b"] = b / 255.0
    if a is not None:
        d["a"] = a
    return d
