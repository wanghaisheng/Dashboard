'''Enable created pages'''

from typing import (
    Dict, Type,
)

from .default import DefaultPageFormat
from .video_downloader import VideoDownloaderPage
from .welcome_page import WelcomePage


STARTING_PAGE = "Welcome"

PAGE_MAP: Dict[str, Type[DefaultPageFormat]] = {
    "Welcome": WelcomePage,
    "Video Downloader": VideoDownloaderPage,
}


__all__ = ["PAGE_MAP"]
