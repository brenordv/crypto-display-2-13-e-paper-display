from pathlib import Path
from typing import Union

from PIL import Image, ImageDraw

from src.image_builder.image_builder_types import ImageBuilderConfig, ImageElementInfo, ImageElementExtraInfo
from src.utils.asset_utils import get_available_images


class ImageBuilder:
    def __init__(self, width: int, height: int, config: ImageBuilderConfig = None):
        self.width = width
        self.height = height
        self.config = config or ImageBuilderConfig()
        self.image = Image.new(
            self.config.image_mode.to_str(),
            (self.width, self.height),
            self.config.background_color
        )
        self.draw = ImageDraw.Draw(self.image)

    def width_to_percent(self, width: Union[int, float]) -> float:
        return width / self.width

    def height_to_percent(self, height: Union[int, float]) -> float:
        return height / self.height

    def add_text(
            self,
            text: str,
            text_type: str,
            x_percent: float,
            y_percent: float,
            color: str = None,
            bold: bool = False,
            font_size_override: int = None,
            font_family_override: str = None
    ) -> ImageElementInfo:
        font, bold_font = self.config.get_font(
            text_type,
            font_size_override=font_size_override,
            font_family_override=font_family_override
        )

        color = color or self.config.default_text_color

        active_font = bold_font if bold else font

        # Get the bounding box of the text
        bbox = self.draw.textbbox((0, 0), text, font=active_font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Calculate the x position
        if x_percent == 0:
            x = 0
        elif x_percent == 1:
            x = self.width - text_width
        else:
            x = int(self.width * x_percent - text_width / 2)

        # Calculate the y position
        ascent, descent = font.getmetrics()
        if y_percent == 0:
            y = 0
        elif y_percent == 1:
            y = self.height - text_height - descent
        else:
            y = int(self.height * y_percent - (ascent + descent) / 2 + descent)

        # Ensure x and y are within image boundaries
        x = max(0, min(x, self.width - text_width))
        y = max(0, min(y, self.height - text_height))

        # Define the position of the text
        position = (x, y)

        # Draw the text
        self.draw.text(position, text, fill=color, font=active_font)

        # Return text position and size info
        return ImageElementInfo(
            x_percent=x_percent,
            y_percent=y_percent,
            x=x,
            y=y,
            width=text_width,
            height=text_height
        )

    def add_outline_square(
            self,
            x_start: float = 0,  # 0 to 1.0 (percentage of image width)
            y_start: float = 0,  # 0 to 1.0 (percentage of image height)
            x_end: float = 1.0,  # 0 to 1.0 (percentage of image width)
            y_end: float = 1.0,  # 0 to 1.0 (percentage of image height)
            border_width: int = 4,
            color: str = "black"
    ) -> ImageElementInfo:
        # Calculate the start and end coordinates
        padding = border_width * 0.10
        x0 = int(self.width * x_start)
        y0 = int(self.height * y_start)
        x1 = int(self.width * x_end) - padding
        y1 = int(self.height * y_end) - padding

        # Draw the outer square
        self.draw.rectangle((x0, y0, x1, y1), outline=color, width=border_width)

        # Calculate the inner coordinates
        inner_x0 = x0 + border_width
        inner_y0 = y0 + border_width
        inner_x1 = x1 - border_width
        inner_y1 = y1 - border_width

        # Draw the inner square to create the hollow effect
        self.draw.rectangle((inner_x0, inner_y0, inner_x1, inner_y1), outline=self.config.background_color)

        # Return square position and size info
        return ImageElementInfo(
            x_percent=x_start,
            y_percent=y_start,
            x_percent_end=x_end,
            y_percent_end=y_end,
            x=x0,
            y=y0,
            width=x1 - x0,
            height=y1 - y0,
            x_end=x1,
            y_end=y1,
            extra=ImageElementExtraInfo(border_width=border_width)
        )

    def add_line(
            self,
            x_start: float,  # 0 to 1.0 (percentage of image width)
            y_start: float,  # 0 to 1.0 (percentage of image height)
            x_end: float,  # 0 to 1.0 (percentage of image width)
            y_end: float,  # 0 to 1.0 (percentage of image height)
            line_width: int = 1,
            color: str = "black"
    ) -> ImageElementInfo:
        # Calculate the start and end coordinates
        x0 = int(self.width * x_start)
        y0 = int(self.height * y_start)
        x1 = int(self.width * x_end)
        y1 = int(self.height * y_end)

        # Draw the line
        self.draw.line([(x0, y0), (x1, y1)], fill=color, width=line_width)

        # Return line position and size info
        return ImageElementInfo(
            x=x0,
            y=y0,
            width=x1 - x0,
            height=y1 - y0,
            x_end=x1,
            y_end=y1
        )

    def add_image(
            self,
            image_path: Union[str, Path],  # Path to the image to add
            x_percent: float = 0,  # 0 to 1.0 (percentage of image width)
            y_percent: float = 0,  # 0 to 1.0 (percentage of image height)
            width_percent: float = 1.0,  # 0 to 1.0 (percentage of image width)
            height_percent: float = 1.0,  # 0 to 1.0 (percentage of image height)
            expand: bool = False,  # If True, resize the image to the specified width and height
            scale: float = 1.0  # Scale factor for the image
    ):
        # Load the image to add
        added_image = Image.open(image_path)

        # Scale the image
        if scale != 1.0:
            new_size = (int(added_image.width * scale), int(added_image.height * scale))
            added_image = added_image.resize(new_size, Image.Resampling.LANCZOS)

        if expand:
            # Calculate the size of the added image
            added_image_width = int(self.width * width_percent)
            added_image_height = int(self.height * height_percent)
            added_image = added_image.resize((added_image_width, added_image_height), Image.Resampling.LANCZOS)
        else:
            added_image_width, added_image_height = added_image.size

        # Calculate the position to paste the added image
        x = int(self.width * x_percent - added_image_width / 2)
        y = int(self.height * y_percent - added_image_height / 2)

        # Ensure x and y are within image boundaries
        x = max(0, min(x, self.width - added_image_width))
        y = max(0, min(y, self.height - added_image_height))

        # Paste the added image onto the main image
        self.image.paste(added_image, (x, y), added_image.convert('RGBA'))

        # Return added image position and size info
        return ImageElementInfo(
            x_percent=x_percent,
            y_percent=y_percent,
            x=x,
            y=y,
            width=added_image_width,
            height=added_image_height
        )

    def build(self) -> Image:
        return self.image


# Example usage:
if __name__ == "__main__":
    builder = ImageBuilder(250, 122)

    builder.add_outline_square(x_end=0.5, y_end=0.5)

    builder.add_line(0, 0, 1, 1, line_width=3, color="red")

    image = get_available_images()["full_heart"]

    builder.add_image(
        image,
        x_percent=1,
        y_percent=1,
        scale=0.2
    )

    builder.add_text(
        text="Hello World!",
        text_type="title",
        x_percent=0,
        y_percent=0
    )

    builder.add_text(
        text="Hello World!",
        text_type="title",
        x_percent=0.5,
        y_percent=0.5
    )

    builder.add_text(
        text="Hello World!",
        text_type="title",
        x_percent=1,
        y_percent=1
    )

    img = builder.build()
    img.show()
