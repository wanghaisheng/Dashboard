#from .video_downloader import VideoDownloaderPage
from .welcome_page import WelcomePage
from .default import DefaultPageFormat

from typing import Dict, Type

STARTING_PAGE = "Welcome"

PAGE_MAP: Dict[str, Type[DefaultPageFormat]] = {
    "Welcome": WelcomePage,
    #"Video Downloader": VideoDownloader,
}

__all__ = ["PAGE_MAP"]