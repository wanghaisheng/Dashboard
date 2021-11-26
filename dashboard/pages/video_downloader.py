'''Simple Video Downloader
Created on: 23/10/21
Created by: @Blastorios'''

from pathlib import Path
from shutil import rmtree
from typing import (
    Dict, Optional,
    Any, Tuple
)

import streamlit as st
from streamlit.elements.progress import ProgressMixin
import yt_dlp as ytdl  # TODO: perhaps use yt_dlp?

from dashboard.pages.default import DefaultPage
from dashboard.utils import DownloadTracker, IsTracked


# Constants
HASH_LENGTH: int = 9    # Length of the reference hash
TTL_TIME: int = 300     # Time in seconds to allow Tracker inside of cache
READ_TYPE: str = 'rb'   # 'read bytes' from a video file


@st.cache(suppress_st_warning = True, ttl = TTL_TIME)
def build_download_tracker(download_folder_path: Path) -> object:
    """
    Construct a download tracker that will be cached for `ttl/60`
    minutes. The ttl is refreshed on every call.
    """
    return DownloadTracker(download_folder_path)


class VideoDownloader:
    """Download Videos through several checks
    and parsers."""
    
    def __init__(self, 
                 reference: str,
                 extension: str,
                 temp_download_path: Path,
                 hash_length: int = HASH_LENGTH,
                 read_type: str = READ_TYPE) -> object:
        self.reference: str = reference  # video UUID
        self.extension: str = extension  # video extension
        self.hash_length: int = hash_length
        self.read_type: str = read_type
        self.video_content: Optional[bytes] = None
        self.video_dir_location: Path = temp_download_path / self.reference
        
        self._create_download_location()
    
    @classmethod
    def from_url(cls, 
                 url: str, 
                 temp_download_path: Path,
                 hash_length: int = HASH_LENGTH) -> object:
        # We only allow urls with https.
        if not url.startswith("https"):
            raise ValueError(f"Cannot create a safe transmission for the url: {url}")
        
        # Parse a subselection of the hash into the cls.
        _hashed_url = str(hash(url))[:hash_length]
        
        new_cls = cls(_hashed_url, temp_download_path, hash_length)
        new_cls.video_url = url
        
        return new_cls
    
    def __del__(self) -> None:
        """Ensure we destroy the tempfile on exit"""
        self._del_temp()
    
    def __eq__(self, other: object) -> bool:
        """Equality check"""
        if other is None: return False
        return self.reference == other.reference
    
    def _del_temp(self) -> None:
        """Delete Temporary Directories
        
        Normally the context manager is sufficient but this
        doesn't work with streamlit. Therefore residing with
        this workaround.
        """
        return rmtree(self.video_dir_location)
    
    def _create_download_location(self) -> None:
        """Create a temporary location for a downloaded video,
        inside of the temp_dir."""
        # _log.info(f"Constructed Temporary Download Folder for {self.reference}")
        if not self.video_dir_location.exists(): 
            self.video_dir_location.mkdir()
        
        return
    
    def download_video(self, 
                       video_url: Optional[str] = None,
                       ydl_options: Optional[Dict[str, Any]] = None,
                       progression: Optional[Dict[str, Any]] = None) -> Tuple[Optional[bytes], Optional[Dict[str, Any]]]:
        """Download the provided video with ytdl."""
        self.video_content: tuple = (None, None)
        
        # Set YDL options appropiately, these options can be updated but
        # we need these default values.
        ydl_opts: Dict[str, Any] = {
            # "format": f"bestvideo[ext={media_type.split('/')[-1]}]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            # "merge-output-format": f"{media_type.split('/')[-1]}",
            'outtmpl': f"{self.video_dir_location}/%(title)s.%(ext)s",
            'verbose': False,
        }
        
        # Update if provided.
        if ydl_options: ydl_opts.update(ydl_options)
        if progression: ydl_opts.update(progression)
        
        # Acquire attribute if we used `from_uuid`
        video_url = getattr(self, 'video_url', video_url)
        
        # Download the requested video
        with ytdl.YoutubeDL(ydl_opts) as video_downloader:
            self.video_metadata = video_downloader.extract_info(
                # Process is False to avoid additional downloading!
                video_url, process = False) 
            
            # TODO: Implement playlist feature.
            # Use the metadata to include a senatizer.
            video_downloader.download([video_url])
        
        self.video_file_path = list(
            Path(self.video_dir_location).glob(f"*.{self.extension}"))[0]
        
        with open(self.video_file_path.resolve(), self.read_type) as video_file:
            self.video_bytes = video_file.read()
            self.video_content = (self.video_bytes, self.video_metadata)
            
        return self.video_content


class VideoDownloaderPage(DefaultPage):
    """Construct a streamlit page to download a video."""
    
    def __init__(self, 
                 temp_dir_name: str = "video_downloads", 
                 ttl_time: int = TTL_TIME,) -> object:
        super().__init__()
        self.ttl_time: int = ttl_time
        self._temp_dir_name: str = temp_dir_name
        
        # DownloadTracker, needs to run after the temp_dir is created
        self.tracker: DownloadTracker = build_download_tracker(self._temp_dir_name)
    
    def _is_allowed(self, url: str) -> bool:
        """Accepted Websites"""
        return "you" in url and "tube" in url
    
    def _check_url(self, url: str) -> bool:
        """Check if we will download over a secure connection,
        we do not download from a list and the provided website
        is allowed."""
        if (url and url.startswith("https") and 
            not 'list' in url and
            self._is_allowed(url)):
            return True
        
        self._error(self.notification_placeholder,
            f"URL invalid: {('Dashboard requires https.' if not url.startswith('https') else 'Link is not supported.')}"
        )
        
        return False
    
    def _display_progression(self, info: Dict[str, Any]) -> None:
        """Display Download Progression."""
        self.progression_bar.progress(
            int((info['downloaded_bytes'] / info['total_bytes'])*100)
        )
        
        return
    
    def _setup_input_form(self) -> bool:
        
        with st.form("Download Specifications"):
            col1, col2 = self._generate_columns()
            
            with col1:
                self.video_url = st.text_input(
                    "URL:",
                    value = "",
                    help = "URL to the video/audio file you wish to download (Required to begin with 'https'!).",
                    key = "video_url")
                
            with col2:
                self.video_uuid = st.text_input(
                    "Unique Identifier as provided by the Dashboard:",
                    value = "",
                    help = "Solely generated by the Dashboard interface. A 9 integer string like: '658437439'.",
                    key = "video_uuid")
            
            st.selectbox("Extension by which to download. (mp3 will force the audio download)",
                           {"mp3", "mp4", "mkv", "webm"}, index = 1)
            
            start_download = st.form_submit_button(
                "Start Download")
        
        return start_download
    
    def _create_download_button(self, video_content: bytes, video_file_path: str) -> None:
        """Create a Download button for a video+audio file.
        
        video_file_path should include a complete Path.resolved() path."""
        st.download_button(
            label = "Download the Video File",
            data = video_content,
            file_name = video_file_path,
            mime = 'application/octet-stream'
        )
        
        return
    
    def write(self) -> None:
        """Start writing the page content"""
        
        # Set the general page functions
        st.title("Video/Audio Downloader")
        
        st.write(f"Simply paste a [supported](https://github.com/youtube_dlp/) videolink \
                into the left box or a video UUID in the right box if you have downloaded \
                the video less than {round(self.ttl_time/60)} minutes ago.")
        
        start_download = self._setup_input_form()
        
        # Ensure we have some placeholders for our content.
        # We use empty so we can clear the section after n-seconds.
        # A container will retain the content.
        self.notification_placeholder = st.empty()
        
        # When the button has been pressed.
        if not start_download: st.stop()
        
        # Button is pressed while all is empty.
        if self.video_url == "" and self.video_uuid == "": st.stop()
        
        # Priority on UUID.
        if self.tracker.is_in_store(self.video_uuid):
            video_bytes, metadata = self.tracker.get_item(
                self.video_uuid).video_content
        
        # If we get a valid URL string:
        elif self._check_url(self.video_url):
            self.progression_bar = st.progress(0)
            video_downloader = VideoDownloader.from_url(self.video_url, self.tracker.temp_directory)
            
            if self.tracker.is_in_store(video_downloader.reference):
                video_bytes, metadata = self.tracker.get_item(video_downloader.reference).video_content
                self.progression_bar.progress(100)
            
            else: video_bytes, metadata = video_downloader.download_video(
                progression = {'progress_hooks': [self._display_progression]})
        
        else: st.stop()
        
        # In case it remains None.
        if video_bytes is None:
            self._error(
                self.notification_placeholder, "Video Download came back empty, halting.")
            st.stop()
        
        self._create_download_button(video_bytes, metadata['title'])
