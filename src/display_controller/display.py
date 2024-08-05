import time
from datetime import datetime
from typing import Union

from PIL.Image import Image
from simple_log_factory.log_factory import log_factory

try:
    from src.drivers.waveshare_epd import epd2in13_V3
except (ImportError, ModuleNotFoundError, OSError):
    pass


class EPaperDisplay(object):
    def __init__(self):
        self._logger = log_factory("EPaperDisplay", unique_handler_types=True)
        self._display = epd2in13_V3.EPD()
        self._first_date: Union[datetime, None] = None
        # Set refresh to a day
        self.refresh_after_seconds = 60 * 60 * 24

    def _process_safety_refresh(self):
        if self._first_date is None:
            self._first_date = datetime.now()
        else:
            now = datetime.now()
            time_diff = now - self._first_date
            if time_diff.total_seconds() >= self.refresh_after_seconds:
                self._logger.info("Refreshing display to prevent burn-in...")
                self.sleep()
                self.off()
                time.sleep(10)
                self._logger.info("Reinitializing display...")
                self._display = epd2in13_V3.EPD()
                self.init_and_clear()
                self._first_date = now

    def init_and_clear(self):
        self._display.init()
        self._display.Clear(0xFF)

    def display(self, image: Image):
        self._process_safety_refresh()
        self._display.display(self._display.getbuffer(image))

    def sleep(self):
        self._display.sleep()

    def off(self):
        epd2in13_V3.epdconfig.module_exit(cleanup=True)


class ShowImageDisplay(object):
    def __init__(self):
        pass

    def init_and_clear(self):
        pass

    def sleep(self):
        pass

    def off(self):
        pass

    @staticmethod
    def display(image: Image):
        image.show()


class DisplayController(object):
    def __init__(self):
        self._logger = log_factory("DisplayController", unique_handler_types=True)
        try:
            self._display = EPaperDisplay()
        except Exception as e:
            self._logger.error(f"Error initializing EPaperDisplay. Falling back to showing image. Error: {e}")
            self._display = ShowImageDisplay()

        self._display.init_and_clear()

    def clear(self):
        self._display.init_and_clear()

    def display(self, data: Image):
        self._display.display(data)

    def wake(self):
        self._display.init_and_clear()

    def sleep(self, sleep_time):
        self._display.sleep()
        time.sleep(sleep_time)
        self._display.init_and_clear()

    def off(self):
        self._display.sleep()
        self._display.off()
        self._logger.info("Display off")