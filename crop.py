from PIL import Image
import os
from pathlib import Path

import PIL

src_dir = Path("ranges")  # dossier racine


def crop_image(path):
    img = Image.open(path)

    cropped_image = img.crop((0, 0, 510, 510))
    cropped_image.save(path)  # écrase l’original


for p in src_dir.rglob("*.png"):
    crop_image(p)
    print("Cropped:", p)
