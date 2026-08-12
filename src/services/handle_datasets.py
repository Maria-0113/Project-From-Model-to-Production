from pathlib import Path
import shutil
import uuid
from datetime import datetime


def move_data(is_drift: bool):

    
    # Folders
    incoming = Path("data/incoming")
    production = Path("data/production")
    archive = Path("data/archive")

    # Create folders if they don't exist
    production.mkdir(exist_ok=True)
    archive.mkdir(exist_ok=True)

    destination_folder = production if is_drift else archive

    # Archive current production files if drift detected
    if is_drift:
        if any(production.glob("*.csv")):
            for file in production.glob("*.csv"):
                shutil.move(file, archive / file.name)
    # Move incoming files
    for file in incoming.glob("*.csv"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        destination = destination_folder / f"creditcard_{timestamp}.csv"
        shutil.move(file, destination)
    
