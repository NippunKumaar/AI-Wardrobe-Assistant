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


def get_dominant_color(image: Image.Image):

    # resize to reduce computation
    image = image.resize((150, 150))

    img_array = np.array(image)

    h, w, _ = img_array.shape

    # crop center region (reduce background influence)
    center_crop = img_array[
    int(h*0.25):int(h*0.75),
    int(w*0.25):int(w*0.75)
    ]

    pixels = center_crop.reshape(-1, 3)

    # KMeans clustering
    kmeans = KMeans(n_clusters=3, random_state=42)
    kmeans.fit(pixels)

    labels = kmeans.labels_
    clusters = kmeans.cluster_centers_

    counts = np.bincount(labels)

    # get top 2 clusters
    top_indices = counts.argsort()[-2:][::-1]

    candidate_clusters = clusters[top_indices]

    dominant_rgb = select_best_cluster(candidate_clusters)

    hsv = rgb_to_hsv(dominant_rgb.reshape(1,1,3)).reshape(3)
    h, s, v = hsv
    r, g, b = dominant_rgb

    return classify_color(h, s, v, r, g, b)


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
    # choose cluster with highest red dominance for brown-like colors
    scores = []

    for r, g, b in clusters:
        score = r - b  # brown has strong red dominance over blue
        scores.append(score)

    return clusters[np.argmax(scores)]