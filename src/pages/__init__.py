from .video_downloader import VideoDownloader
from utils import Page

from typing import Dict, Type


PAGE_MAP: Dict[str, Type[Page]] = {
    "Video Downloader": VideoDownloader,
}

__all__ = ["PAGE_MAP"]