'''Simple Video Downloader
Created on: 23/10/21
Created by: @Blastorios'''

from dataclasses import dataclass, field
from pathlib import Path
from shutil import rmtree
from typing import (
    Dict, List, Optional,
    Union, Any,
)

import streamlit as st
import youtube_dl as ytdl

from .default import DefaultPage


# Constants
TTL_TIME: int = 300


@dataclass
class DownloadTracker:
    """
    DownloadTracker, responsible for updating and managing
    the download folder.
    """
    
    temp_directory: Path
    store: tuple = field(default_factory = tuple, compare = True)
    max_folder_size: int = field(
        default = (1024 * 1024 * 1024) * 15, repr = False)  # 15GB
    
    def __del__(self) -> None:
        """Delete the temporary directory."""
        self._del_temp_dir()
        
        return
    
    def _del_temp_dir(self) -> None:
        """Delete the temporary directory."""
        try: rmtree(self.temp_directory)
        except AttributeError: pass
        
        return
    
    def _check_folder_size(self) -> bool:
        """Check if the folder size is greater than the
        maximum allowed size."""
        
        return self.temp_directory.stat().st_size > self.max_folder_size
    
    def is_in_store(self, item: object) -> bool:
        """Check if the item is in the tracker."""
        
        return item in self.store
    
    def get_item(self, item: object) -> object:
        """Get the item from the tracker."""
        
        self.temp_access = self.store[self.store.index(item)]
        
        return self.temp_access

    def add_item(self, item: object) -> None:
        """Append a new item to the tracker."""
        if self._check_folder_size():
            self.del_item()
            
        if not self.is_in_store(item):
            self.store += (item,)
            
            # when we insert a new item
            return True
        # when we do not need to insert it
        return False
    
    def del_item(self, reset_temp: bool = True) -> None:
        """Delete the first item from tracker. This will
        automatically invoke the del thundermethod from the
        stored VideoDownloader object and remove its folder
        from the disk."""
        if reset_temp: self.temp_access = None
        self.store = self.store[1:]
        
        return


class VideoDownloader(object):
    """Construct to Download Videos"""
    
    def __init__(self, 
                 reference: str,
                 temp_download_path: Path) -> object:
        self.reference = reference
        self.is_url = self.reference.startswith("https")
        self.video_dir_location = temp_download_path / self.reference.split("=")[-1]
        self.done = True  # `create location` will change this if necessary
        self._create_download_location()
    
    def __del__(self) -> None:
        """Ensure we destroy the tempfile on exit"""
        self.del_temp()
    
    def _create_download_location(self) -> None:
        """Create a temporary location for a downloaded video,
        inside of the temp_dir."""
        if not self.video_dir_location.exists(): 
            self.video_dir_location.mkdir()
            self.done = False
        
        return
    
    def del_temp(self) -> None:
        """Delete Temporary Directories
        
        Normally the context manager is sufficient but this
        doesn't work with streamlit. Therefore residing with
        this workaround.
        """
        try: rmtree(self.video_dir_location)
        except AttributeError: pass
        
        return
    
    @classmethod
    def from_url(cls, url: str, pathing: Path) -> object:
        if not 'https' in url:
            raise ValueError(f"Cannot create a safe transmission for the url: {url}")
        
        # Not found, start the download!
        downloader = cls(url, pathing)
        
        return downloader
        
    
    @classmethod
    def from_uuid(cls, uuid: str, pathing: Path) -> object:
        downloaded = cls(uuid, pathing)
        
        if downloaded.done:
            return downloaded.video_content
        else:
            return None
    
    def download_video(self,
                 ydl_options: Dict[str, Any],
                 progression: Optional[dict]) -> Union[bytes, bool]:
        """Download the provided video with ytdl."""
        
        # Set YDL options appropiately
        ydl_opts = {
            # "format": f"bestvideo[ext={media_type.split('/')[-1]}]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            # "merge-output-format": f"{media_type.split('/')[-1]}",
            'outtmpl': f"{self.video_dir_location}/%(title)s.%(ext)s",
            'verbose': False,
        }
        
        if ydl_options: ydl_opts.update(ydl_options)
        if progression: ydl_opts.update(progression)
        
        # Download the requested video
        with ytdl.YoutubeDL(ydl_opts) as video_downloader:
            
            if ydl_opts['outtmpl']:
                video_downloader.download([self.url_or_uuid])
        
        self.video_file_name = ydl_opts['filename']
        
        # YoutubeDL always downloads the file to disk
        with open(self.video_dir_location / self.video_file_name, 'rb') as video_file:
            self.video_content = video_file.read()
            
        return self.video_content


@st.cache(suppress_st_warning = True, ttl = TTL_TIME)
def build_download_tracker(download_folder_path: Path) -> object:
    """
    Construct a download tracker that will be cached for ttl/60 mins
    in RAM. The construct will be removed when no one puts an access
    call on it for the TTL_TIME specified.
    """
    return DownloadTracker(download_folder_path)


class VideoDownloaderPage(DefaultPage):
    """Construct a streamlit page to download a video."""
    
    
    def __init__(self, 
                 temp_dir_name: str = "video_downloads", 
                 ttl_time: int = TTL_TIME) -> object:
        super().__init__()
        self.ttl_time = ttl_time
        self.temp_dir_name = temp_dir_name
        # Force location over all constructs
        self.location = Path(".").cwd()
        
        # Build environment
        self._create_temp_dir()
        
        # DownloadTracker, needs to run after the temp_dir is created
        self.tracker = build_download_tracker(self.temp_dir)
    
    def _create_temp_dir(self) -> None:
        """Create a download folder in which we can store
        videodownloader objects and keep track of its size."""
        try:
            if self.temp_dir.exists(): return
        except AttributeError: pass
        
        self.temp_dir = self.location / self.temp_dir_name
        self.temp_dir.mkdir(exist_ok=False)
        
        return
    
    def check_url(self, url: str) -> bool:
        """Check if we will download over a secure connection."""
        
        return "https" in url
    
    def display_progression(self, info: Dict[str, str]) -> None:
        """Display Download Progression."""
        self.notification_placeholder.progress(
            int((info['downloaded_bytes'] / info['total_bytes'])*100)
        )
        
        return
    
    def create_input_boxes(self) -> bool:
        col1, col2 = self.generate_columns()
        sub_col1, sub_col2 = self.generate_columns()
        
        with col1:
            self.video_uuid = st.text_input(
                "Video name as provided by the Dashboard:",
                value = "",
                help = "A name that was provided with a downloaded video.",
                key = "video_uuid")
            
        with col2:
            self.video_url = st.text_input(
                "Video URL (ignored if name is used):",
                value = "",
                help = "URL to the video you wish to download (Needs to start with 'https').",
                key = "video_url")
        
        with sub_col1:
            download_video = st.button(
                "Download Video",
                key = "download_button")
        
        return download_video, sub_col2
    
    def create_download_button(self, video_content: bytes) -> None:
        """Create a Download button for a video+audio file."""
        st.download_button(
            label = "Download the Video File",
            data = video_content,
            file_name = f"{self.ytdl_filename}.mp4",
            mime = 'application/octet-stream'
        )
        
        return
    
    # def initiate_download(self,
    #                       reference: str,
    #                       notifications) -> Optional[bytes]:
        
    #     # Build Downloader
    #     if self.tracker.add_item(VideoDownloader(reference, self.location)):
    #         video_file = self.tracker.store[-1]
    #     else: 
    #         video_file = self.tracker.store[
    #             self.tracker.store.index(VideoDownloader(reference))]
            
    #     video_content = video_file.download(
    #             # Byte stream for the download button
    #             {'progress_hooks': [self.display_progression]})
        
    #     del video_file
        
    #     return video_content
    
    def write(self) -> None:
        """Start writing the page content"""
        
        # Set the general page functions
        st.title("Video Downloader")
        
        download_video, sub_col2 = self.create_input_boxes()
        
        # Ensure we have some placeholders for our content
        self.notification_placeholder = st.container()
        
        # When the button has been pressed:
        if not download_video:
            st.stop()
        
        # Button is pressed while all is empty:
        if self.video_url == "" and self.video_name == "":
            st.stop()
        
        # If we get a valid URL string:
        if self.video_url and self.check_url(self.video_url):
            self.reference = self.video_url
        
        # If we do not get a valid URL
        elif self.video_url:
            self.notification_placeholder.warning(
                "Please use a 'https' link.")
            st.stop()
        
        elif "list" in self.video_url:
            self.notification_placeholder.warning(
                "We do not support playlists at this point in time.")
            st.stop()
        
        # An UUID has priority over an URL
        if self.video_name:
            self.reference = self.video_name
        
        video_content = self.initiate_download(
            self.reference, self.notification_placeholder)
        
        with sub_col2:
            self.create_download_button(video_content)
