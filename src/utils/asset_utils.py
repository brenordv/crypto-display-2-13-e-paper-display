from pathlib import Path
from typing import Dict

from simple_log_factory.log_factory import log_factory

from src.config import IMAGES_FOLDER

__logger = log_factory("asset_utils", unique_handler_types=True)


def get_available_images() -> Dict[str, Path]:
    """
    Get all available images in the images folder.

    :return: A dictionary of image names to image paths.
    """
    # Get all files from the images folder:
    images = IMAGES_FOLDER.glob("*")

    image_dict = {}

    # Create a dictionary of image names to image paths:
    for image in images:
        if not image.is_file():
            __logger.warning(f"Skipping {image} as it is not a file.")
            continue

        if image.suffix.lower() not in [".png", ".jpg", ".jpeg", ".bmp", ".gif"]:
            __logger.warning(f"Skipping {image} as it is not a valid image file.")

        if image.stem in image_dict:
            __logger.warning(f"Skipping {image} as it has the same name as another image.")
            continue

        image_dict[image.stem] = image

    return image_dict
