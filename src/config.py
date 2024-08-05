from pathlib import Path

ROOT_FOLDER = Path(__file__).parent.parent
DATA_FOLDER = ROOT_FOLDER.joinpath(".data")
IMAGES_FOLDER = DATA_FOLDER.joinpath("images")
FONTS_FOLDER = DATA_FOLDER.joinpath("fonts")
ROBOTO_FONT_FOLDER = FONTS_FOLDER.joinpath("Roboto")

FONT_ARIAL = FONTS_FOLDER.joinpath("arial.ttf")
FONT_ARIAL_BOLD = FONTS_FOLDER.joinpath("arialbd.ttf")
FONT_ROBOTO_REGULAR = ROBOTO_FONT_FOLDER.joinpath("Roboto-Regular.ttf")
FONT_ROBOTO_BOLD = ROBOTO_FONT_FOLDER.joinpath("Roboto-Bold.ttf")

#TODO: Check if fonts exist

# That's the one we're using in this project
WAVESHARE_DISPLAY = "Waveshare 2.13inches e-Paper"

DISPLAY_SIZES = {
    WAVESHARE_DISPLAY: (250, 122),
}

creatable_folder = [DATA_FOLDER, IMAGES_FOLDER, FONTS_FOLDER, ROBOTO_FONT_FOLDER]
for folder in creatable_folder:
    if folder.exists():
        continue
    folder.mkdir(exist_ok=True)
