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

    # count cluster sizes
    counts = np.bincount(labels)

    # pick largest cluster (most dominant area)
    dominant_rgb = clusters[np.argmax(counts)]

    hsv = rgb_to_hsv(dominant_rgb.reshape(1,1,3)).reshape(3)
    h, s, v = hsv

    return classify_color(h, s, v)


def classify_color(h, s, v):

    # handle neutral colors first
    if s < 0.25:
        if v > 0.8:
            return "white"
        elif v > 0.4:
            return "grey"
        else:
            return "black"

    # hue-based classification
    if h < 15 or h >= 345:
        return "red"
    elif h < 35:
        return "orange"
    elif h < 55:
        return "yellow"
    elif h < 85:
        return "green"
    elif h < 140:
        return "blue"
    elif h < 170:
        return "purple"
    else:
        return "pink"