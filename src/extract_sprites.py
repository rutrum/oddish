import numpy as np
import matplotlib.pylab as plt
import toml

def load_config():
    return toml.load("config.toml")

def remove_background(im):
    (w, h, _) = im.shape
    im = np.dstack((im, np.full((w, h), 1.0)))
    bg_color = np.copy(im[0, 0])
    for x in range(w):
        for y in range(h):
            if (im[x, y] == bg_color).all():
                im[x, y] = [0, 0, 0, 0]
    return im

def main():
    config = load_config()
    sheet = plt.imread(config["sprite_sheet"])
    (h, w, _) = (sheet.shape)

    total = 0

    for x in range(1,w-160,161):
        offset = 0
        count = 0
        for y in range(1,h-64,65):
            total += 1
            if total > 151:
                break
            count += 1
            y = y + offset
            sprite = sheet[y:y+64, x:x+64]
            sprite = remove_background(sprite)
            plt.imsave(f"{config['sprites_path']}/{total:03d}.png", sprite)
            if count % 3 == 0:
                offset += 2
    print(f"Wrote {total} sprites to {config['sprites_path']}.")

if __name__ == '__main__':
    main()
