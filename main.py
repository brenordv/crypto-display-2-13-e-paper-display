import logging
from datetime import datetime
from pathlib import Path

from PIL.Image import Image
from simple_log_factory.log_factory import log_factory

from src.config import WAVESHARE_DISPLAY, DISPLAY_SIZES
from src.data_fetchers.crypto_value_fetcher import get_current_crypto_value
from src.data_fetchers.mined_value_fetcher import get_current_mined_value
from src.display_controller.display import DisplayController
from src.image_builder.image_builder import ImageBuilder
from src.image_builder.image_builder_types import ImageElementInfo
from src.utils.asset_utils import get_available_images


def _add_border(builder: ImageBuilder) -> ImageElementInfo:
    return builder.add_outline_square(
        x_start=0.005,
        y_start=0.01,
        x_end=0.999,
        y_end=0.995,
        border_width=5)


def _add_monero_icon(builder: ImageBuilder, monero_icon: Path, outline_info: ImageElementInfo) -> ImageElementInfo:
    prev_x = builder.width_to_percent(outline_info.x + outline_info.extra.border_width)
    prev_y = builder.height_to_percent(outline_info.y + outline_info.extra.border_width)
    position_adjust_x = 0.12
    position_adjust_y = 0.24

    return builder.add_image(
        image_path=monero_icon,
        x_percent=prev_x + position_adjust_x,
        y_percent=prev_y + position_adjust_y,
        scale=0.1
    )


def _add_wallet_value(builder: ImageBuilder, wallet_value: str, wallet_icon_info: ImageElementInfo) -> ImageElementInfo:
    prev_y = builder.height_to_percent(wallet_icon_info.y)
    position_adjust_y = 0.1

    return builder.add_text(
        text=wallet_value,
        text_type="title",
        bold=True,
        x_percent=0.62,
        y_percent=prev_y + position_adjust_y,
        font_size_override=31
    )


def _add_wallet_worth_value(builder: ImageBuilder, wallet_worth_value_str: str, wallet_value_info: ImageElementInfo) -> ImageElementInfo:
    prev_y = builder.height_to_percent(wallet_value_info.y + wallet_value_info.height)
    position_adjust_y = 0.14

    return builder.add_text(
        text=wallet_worth_value_str,
        text_type="subtitle",
        x_percent=0.725,
        y_percent=prev_y + position_adjust_y,
    )


def _add_wallet_value_label(builder: ImageBuilder, label: str, wallet_value_info: ImageElementInfo) -> ImageElementInfo:
    prev_y = builder.height_to_percent(wallet_value_info.y + wallet_value_info.height)

    position_adjust_y = 0.10

    return builder.add_text(
        text=label,
        text_type="body",
        x_percent=0.895,
        y_percent=prev_y + position_adjust_y,
    )


def _add_wallet_worth_label(builder: ImageBuilder, label: str, wallet_worth_value_info: ImageElementInfo) -> ImageElementInfo:
    prev_y = builder.height_to_percent(wallet_worth_value_info.y + wallet_worth_value_info.height)

    position_adjust_y = 0.10

    return builder.add_text(
        text=label,
        text_type="body",
        x_percent=0.9,
        y_percent=prev_y + position_adjust_y,
    )


def _add_status_text(builder: ImageBuilder, status_text: str, outline_info: ImageElementInfo) -> ImageElementInfo:
    prev_y = builder.height_to_percent(outline_info.y_end)
    y = prev_y - 0.12

    return builder.add_text(
        text=status_text,
        text_type="caption",
        x_percent=0.5,
        y_percent=y,
    )


def _add_monero_value_info(builder: ImageBuilder, monero_usd_value: str, monero_icon_info: ImageElementInfo) -> ImageElementInfo:
    prev_x = builder.width_to_percent(monero_icon_info.x)
    prev_y = builder.height_to_percent(monero_icon_info.y + monero_icon_info.height)
    position_adjust_x = 0.13
    position_adjust_y = 0.095

    return builder.add_text(
        text=monero_usd_value,
        text_type="subtitle",
        x_percent=prev_x + position_adjust_x,
        y_percent=prev_y + position_adjust_y,
    )


def _add_monero_value_label(builder: ImageBuilder, label: str, monero_value_info: ImageElementInfo) -> ImageElementInfo:
    prev_x = builder.width_to_percent(monero_value_info.x)
    prev_y = builder.height_to_percent(monero_value_info.y + monero_value_info.height)
    position_adjust_x = 0.15
    position_adjust_y = 0.225

    return builder.add_text(
        text=label,
        text_type="body",
        x_percent=prev_x + position_adjust_x,
        y_percent=prev_y + position_adjust_y,
    )


def _add_last_updated(builder: ImageBuilder, last_updated_text: str, status_text_info: ImageElementInfo) -> ImageElementInfo:
    y = status_text_info.y_percent

    return builder.add_text(
        text=last_updated_text,
        text_type="caption",
        x_percent=0.86,
        y_percent=y,
    )


def draw_image(wallet_value: float, monero_usd_value: float, status_text: str) -> Image:
    width, height = DISPLAY_SIZES.get(WAVESHARE_DISPLAY)
    available_images = get_available_images()
    builder = ImageBuilder(width, height)

    outline_info = _add_border(builder)

    monero_icon = available_images.get("monero(1)")

    monero_icon_info = _add_monero_icon(builder, monero_icon, outline_info)

    wallet_value_str = f"{wallet_value:.8f}"

    wallet_value_info = _add_wallet_value(builder, wallet_value_str, monero_icon_info)
    wallet_value_label_info = _add_wallet_value_label(builder, "XMR", wallet_value_info)

    monero_value_label_info = _add_monero_value_label(builder, "1 XMR > USD", monero_icon_info)
    monero_value_info = _add_monero_value_info(builder, f"${monero_usd_value:.2f}", monero_value_label_info)

    wallet_worth_value = wallet_value * monero_usd_value
    wallet_worth_value_str = f"{wallet_worth_value:.10f}"

    wallet_worth_value_info = _add_wallet_worth_value(builder, wallet_worth_value_str, wallet_value_label_info)

    wallet_worth_label_info = _add_wallet_worth_label(builder, "USD", wallet_worth_value_info)

    last_updated = datetime.now()
    status_text_info = _add_status_text(builder, status_text, outline_info)

    last_updated_text = last_updated.strftime("%H:%M:%S")
    last_updated_text_info = _add_last_updated(builder, last_updated_text, status_text_info)

    img = builder.build()
    return img


def main():
    logging.basicConfig(level=logging.INFO)
    logger = log_factory("Main", unique_handler_types=True)
    delay_between_updates = 10 * 60  # 10 minutes
    display_controller = None

    try:
        display_controller = DisplayController()
        while True:
            monero_usd_value = get_current_crypto_value()
            wallet_value = get_current_mined_value()
            img = draw_image(wallet_value, monero_usd_value, "Idle")

            display_controller.display(img)

            display_controller.sleep(delay_between_updates)

            img = draw_image(wallet_value, monero_usd_value, "Updating")
            display_controller.display(img)

    except KeyboardInterrupt:
        logger.info("User Exiting")

    except Exception as e:
        logger.error(f"Error: {e}")

    finally:
        if display_controller is not None:
            display_controller.off()


if __name__ == '__main__':
    main()
