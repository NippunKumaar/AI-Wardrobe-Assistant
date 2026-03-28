import numpy as np
from PIL import Image
from sklearn.cluster import KMeans



def rgb_to_hsv(image_array):
    # normalize RGB values
    image_array = image_array / 255.0

    r, g, b = image_array[..., 0], image_array[..., 1], image_array[..., 2]

    cmax = np.max(image_array, axis=-1)
    cmin = np.min(image_array, axis=-1)
    delta = cmax - cmin

    hue = np.zeros_like(cmax)

    mask = delta != 0

    idx = (cmax == r) & mask
    hue[idx] = (60 * ((g[idx] - b[idx]) / delta[idx]) + 360) % 360

    idx = (cmax == g) & mask
    hue[idx] = (60 * ((b[idx] - r[idx]) / delta[idx]) + 120)

    idx = (cmax == b) & mask
    hue[idx] = (60 * ((r[idx] - g[idx]) / delta[idx]) + 240)

    saturation = np.zeros_like(cmax)
    saturation[cmax != 0] = delta[cmax != 0] / cmax[cmax != 0]

    value = cmax

    hsv = np.stack([hue, saturation, value], axis=-1)
    return hsv


def get_dominant_color(image):

    # resize
    image = image.resize((150, 150))
    img_array = np.array(image)

    h, w, _ = img_array.shape

    # tighter center crop (important)
    crop = img_array[
        int(h*0.35):int(h*0.65),
        int(w*0.35):int(w*0.65)
    ]

    # flatten pixels
    pixels = crop.reshape(-1, 3)

    # take median color (robust to noise)
    median_rgb = np.median(pixels, axis=0)

    r, g, b = median_rgb

    # convert to HSV
    hsv = rgb_to_hsv(median_rgb.reshape(1,1,3)).reshape(3)
    h, s, v = hsv

    color = classify_color(h, s, v, r, g, b)
    family = map_to_family(color)

    return color, family


def classify_color(h, s, v, r,g, b):

    if r > 80 and g > 40 and b < 100 and r > g > b:
        return "brown"

    # 1. Very dark → black
    if v < 0.2:
        return "black"

    # 2. Light blue fix (critical)
    if 180 <= h <= 260 and s < 0.4 and v > 0.7:
        return "blue"

    # 3. Neutral colors
    if s < 0.25:
        if v > 0.85:
            return "white"
        elif v > 0.35:
            return "grey"
        else:
            return "black"

    
    # Improved brown detection
    if 10 < h < 50 and v < 0.85 and s > 0.35:
        return "brown"

    # 5. Blue
    if 180 <= h <= 260:
        return "blue"

    # 6. Red / Pink
    if h < 10 or h > 340:
        return "red"
    if 300 <= h <= 340:
        return "pink"

    # beige / cream detection (optional refinement)
    if 20 < h < 50 and s < 0.35 and v > 0.75:
        return "beige"

    # 7. Remaining colors
    if 10 <= h < 45:
        return "orange"
    elif 45 <= h < 70:
        return "yellow"
    elif 70 <= h < 160:
        return "green"
    elif 260 < h < 300:
        return "purple"

    return "unknown"

def select_best_cluster(clusters):
    scores = []

    for r, g, b in clusters:
        # compute simple saturation proxy
        max_c = max(r, g, b)
        min_c = min(r, g, b)
        saturation = (max_c - min_c) / (max_c + 1e-5)

        # scoring:
        # prefer clusters with:
        # - moderate brightness
        # - lower saturation (for neutrals)
        # - but not too dark

        brightness = (r + g + b) / 3

        score = (
            (1 - saturation) * 0.6 +   # prefer low saturation
            (brightness / 255) * 0.4   # prefer visible brightness
        )

        scores.append(score)

    return clusters[np.argmax(scores)]


def map_to_family(color):

    mapping = {
        "black": "dark_neutral",
        "grey": "dark_neutral",
        "white": "light_neutral",

        "blue": "blue_family",

        "brown": "earth_tones",
        "yellow": "earth_tones",
        "orange": "earth_tones",

        "red": "warm_colors",
        "pink": "warm_colors",

        "green": "cool_colors",
        "purple": "cool_colors"
    }
    return mapping.get(color, "unknown")