from pathlib import Path
from typing import Optional, Union, Tuple
from pydantic.dataclasses import dataclass
from enum import Enum

from PIL import ImageFont

from simple_log_factory.log_factory import log_factory

from src.config import FONT_ROBOTO_REGULAR, FONT_ROBOTO_BOLD


class ImageMode(Enum):
    ONE_BIT = "1"  # Black and white (1-bit pixels)
    GRAYSCALE = "L"  # Grayscale (8-bit pixels)
    PALETTE = "P"  # Palette-based image (8-bit pixels, mapped to any other mode using a color palette)
    RGB = "RGB"  # True color (24-bit, 3x8-bit pixels)
    RGBA = "RGBA"  # True color with alpha channel (32-bit, 4x8-bit pixels)
    CMYK = "CMYK"  # Color separation (32-bit, 4x8-bit pixels)
    YCbCr = "YCbCr"  # Color video format (24-bit, 3x8-bit pixels)
    LAB = "LAB"  # Lab color space (24-bit, 3x8-bit pixels)
    HSV = "HSV"  # Hue, Saturation, Value color space (24-bit, 3x8-bit pixels)
    INTEGER = "I"  # 32-bit signed integer pixels
    FLOAT = "F"  # 32-bit floating point pixels

    def to_str(self) -> str:
        return str(self.value)

    @classmethod
    def is_valid(cls, value):
        if isinstance(value, cls):
            return True
        if isinstance(value, str) and value in cls._value2member_map_:
            return True
        return False


@dataclass(frozen=True)
class ConfigFontSizes:
    title: Optional[int] = 24
    subtitle: Optional[int] = 18
    body: Optional[int] = 14
    caption: Optional[int] = 12


@dataclass
class ImageBuilderConfig:
    __logger = log_factory("ImageBuilderConfig", unique_handler_types=True)
    background_color: Optional[str] = "white"
    default_text_color: Optional[str] = "black"
    default_font: Optional[Union[str, Path]] = FONT_ROBOTO_REGULAR
    default_font_bold: Optional[Union[str, Path]] = FONT_ROBOTO_BOLD
    image_mode: Optional[ImageMode] = ImageMode.RGBA
    default_font_sizes: Optional[ConfigFontSizes] = None

    def __post_init__(self):
        self.default_font_sizes = self.default_font_sizes or ConfigFontSizes()

        if not ImageMode.is_valid(self.image_mode):
            self.__logger.error(f"Invalid image mode {self.image_mode}. Using default image mode: RGB.")
            self.image_mode = ImageMode.RGB

    def get_font(
            self,
            font_type: str,
            font_size_override: Optional[int] = None,
            font_family_override: Optional[str] = None,
            bold_font_family_override: Optional[str] = None
    ) -> Tuple[ImageFont, ImageFont]:
        font_family = font_family_override or self.default_font
        bold_font_family = bold_font_family_override or self.default_font_bold
        font_size = font_size_override or getattr(self.default_font_sizes, font_type)
        try:
            regular_font = ImageFont.truetype(font_family, font_size)
            bold_font = ImageFont.truetype(bold_font_family, font_size)
            return regular_font, bold_font
        except IOError:
            self.__logger.error(f"Could not load font {font_family}. Using default font.")
            default_font = ImageFont.load_default()
            return default_font, default_font


@dataclass(frozen=True)
class ImageElementExtraInfo:
    border_width: Optional[int] = None


@dataclass(frozen=True)
class ImageElementInfo:
    x: float
    y: float
    width: float
    height: float
    x_end: Optional[Union[float, None]] = None
    y_end: Optional[Union[float, None]] = None
    x_percent: Optional[Union[float, None]] = None
    y_percent: Optional[Union[float, None]] = None
    x_percent_end: Optional[Union[float, None]] = None
    y_percent_end: Optional[Union[float, None]] = None
    extra: Optional[ImageElementExtraInfo] = None
