import numpy as np
import toml
from PIL import Image
import sys
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import colorsys
import math

class Color:
    def __init__(self, values):
        self.rgb = np.asarray(values[:3])
        self.alpha = 255
        if len(values) == 4:
            self.alpha = values[3]
        self.hsv = colorsys.rgb_to_hsv(*self.rgb / 255.0)

    def __repr__(self):
        return self.hex_code()

    def hex_code(self, prefix=""):
        return prefix + "".join([f"{c:02x}" for c in self.rgb])

    def hue_circle(self):
        angle = self.hsv[0] * 2 * np.pi
        return np.asarray([ np.cos(angle), np.sin(angle) ])

    def rgba(self):
        return np.asarray([ *self.rgb, self.alpha ])


def avg_color(colors):
    avg = np.zeros(3)
    print(avg)
    for color in colors:
        avg += color.rgb
        print(avg)
    return Color((avg / len(colors)).astype(int))


def load_config():
    return toml.load("config.toml")

def read_args():
    if len(sys.argv) < 2:
        print("Too few args")
        exit()
    return {
        "num": sys.argv[1]
    }

def load_image(num, sprites_path):
    path = f"{sprites_path}/{num}.png"
    return Image.open(path)


def print_colors(colors):
    for color in colors:
        print(color.hex_code("#"))


def find_colors(im):
    colors = {}
    width, height = im.size
    print(im.size)
    for x in range(width):
        for y in range(height):
            pxl = im.getpixel((x, y))
            if pxl[3] > 0:
                if pxl in colors:
                    colors[pxl] += 1
                else:
                    colors[pxl] = 0
    return { Color(c): v for c, v in colors.items() }


def plot_colors(colors, ax, groups=None):
    hues = [ c.hsv[0] for c in colors ]
    saturations = [ c.hsv[1] for c in colors ]

    color_groups = {}
    for color, group in zip(colors, groups):
        if group in color_groups:
            color_groups[group].append(color)
        else:
            color_groups[group] = [ color ]

    avg_colors = { i: avg_color(cs).hex_code('#') for i, cs in color_groups.items() }

    for i, (hue, sat) in enumerate(zip(hues, saturations)):
        x = hue
        y = sat
        cs = [ avg_colors[groups[i]] ]
        ax.scatter([x], [y], c=cs, s=1000)


def get_hs_coords(hue, sat):
    angle = (hue % 1) * 2 * np.pi
    return ( np.cos(angle) * sat, np.sin(angle) * sat )


def partition_colors(colors, ks):
    points = [ c.hue_circle() for c in colors ]
    best_score = None
    best_groups = None
    for k in ks:
        kmeans = KMeans(k)
        groups = kmeans.fit_predict(points)
        score = silhouette_score(points, groups)
        if best_score == None or score > best_score:
            best_score = score
            best_groups = groups
    print(best_groups)
    return best_groups


def sort_colors(colors, classification):
    groups = np.zeros(len(np.unique(classification)))
    groups = [ [] for g in groups ]
    for (c, g) in zip(colors, classification):
        groups[g].append(c)

    for g in groups:
        g.sort(key=lambda x: x.hsv[1])

    return groups


def plot_groupings(groupings, im):

    width = len(groupings)
    height = max([ len(g) for g in groupings ])

    A = np.zeros((width, height, 4))
    for x, colors in enumerate(groupings):
        for y, c in enumerate(colors):
            A[x, y] = c.rgba()

    A = A / 255.0
    fig, axs = plt.subplot_mosaic([
        ['NW', 'NE'],
        ['SW', 'SE']
    ])
    axs['NW'].imshow(A)
    axs['NE'].imshow(im)

    return axs

def color_adjacency(im, ax, colors):
    total_colors = len(colors)
    color_list = list(colors)
    color_index_lookup = { c.hex_code(): i for i, c in enumerate(color_list) }
    print(color_list)
    counts = np.zeros((total_colors, total_colors))
    h, w = im.size

    # vertical scan
    for x in range(w):
        for y in range(h-1):
            top = Color(im.getpixel((x, y)))
            bot = Color(im.getpixel((x, y + 1)))
            if top.alpha > 0 and bot.alpha > 0:
                top_idx = color_index_lookup[top.hex_code()]
                bot_idx = color_index_lookup[bot.hex_code()]
                counts[top_idx, bot_idx] += 1
                counts[bot_idx, top_idx] += 1

    # horizontal scan
    for y in range(h):
        for x in range(w-1):
            top = Color(im.getpixel((x, y)))
            bot = Color(im.getpixel((x + 1, y)))
            if top.alpha > 0 and bot.alpha > 0:
                top_idx = color_index_lookup[top.hex_code()]
                bot_idx = color_index_lookup[bot.hex_code()]
                counts[top_idx, bot_idx] += 1
                counts[bot_idx, top_idx] += 1

    ax.imshow(counts)

def main():
    config = load_config()
    args = read_args()

    im = load_image(args["num"], config["sprites_path"])

    colors = find_colors(im)

    groups = partition_colors(colors, config["clusters"])

    groupings = sort_colors(colors, groups)

    axs = plot_groupings(groupings, im)
    plot_colors(colors, axs['SW'], groups)
    color_adjacency(im, axs['SE'], colors)
    plt.show()

if __name__ == '__main__':
    main()
