from PIL import Image
import os
from pathlib import Path

import PIL

src_dir = Path("ranges")  # dossier racine


def crop_image(path):
    img = Image.open(path)
    if img.size != (510, 510):
        cropped_image = img.crop((75, 445, 585, 955))
        print("Cropped:", p)
        cropped_image.save(path)  # écrase l’original


for p in src_dir.rglob("*.png"):
    crop_image(p)
