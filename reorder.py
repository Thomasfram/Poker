import os
import shutil
from pathlib import Path

base = Path("ranges")  # adapte si nécessaire

for depth_dir in base.iterdir():  # ex: 100bb, 40bb…
    if not depth_dir.is_dir():
        continue
    for action_dir in depth_dir.iterdir():  # ex: Open, Vs3bet…
        if not action_dir.is_dir():
            continue
        for file in action_dir.iterdir():  # ex: BTN.png, CO.png…
            if file.is_file():
                position = file.stem  # BTN, CO, etc.
                new_dir = depth_dir / position
                new_dir.mkdir(parents=True, exist_ok=True)
                # le nouveau nom du fichier sera Action.png
                new_file = new_dir / f"{action_dir.name}.png"
                shutil.move(str(file), str(new_file))
        # supprimer l’ancien dossier d’action une fois vide
        shutil.rmtree(action_dir)
