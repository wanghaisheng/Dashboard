'''Simple YouTube Downloader
Created on: 23/10/21
Created by: @Blastorios'''

import base64
import tempfile
import shutil

from pathlib import Path
from time import sleep

import streamlit as st
import youtube_dl as ytdl

from default import DefaultPage
from .utils import Page


class VideoDownloaderPage(DefaultPage, metaclass=Page):
    """Construct a streamlit page."""
    
    def __init__(self):
        super().__init__()
        pass
    
    def write(self):
        """Start writing the page content"""
        
        # Set the general page functions
        st.title("Video Downloader")
        video_url = st.text_input("", 
                                  help = "Insert your desired Video url",
                                  key = "video_url")

        # Layout for the Button and Balloon Check
        download_col, balloon_col = self.__generate_columns()
        with down_col:
            downloading = st.button("Download")
        with balloon_col:
            balloon_check = st.checkbox("Balloons")

        # Ensure we have some placeholders for our content
        notification_placeholder = st.empty()

        # Remember the previous video, easier session control
        self.state.client_config["video_url"] = video_url

        # Check if the parsed URL is a legitimate YouTube link
        checked, url = self.__check_url(self.state.client_config["video_url"])

        # Initialize the downloading process if all requirements pass
        if downloading:
            self.__del_temp()
            if checked:
                self.present_items(
                    url, notification_placeholder, balloon_check)
            else:
                if url != "":
                    st.warning(
                        "YouTube only :unamused::point_up:")
                    st.stop()
                st.stop()
        else:
            st.stop()


class VideoDownloader(object):
    """Construct to Download Videos"""
    
    def __init__(self, state) -> object:
        self.base_path = Path().cwd()
        self.ytdl_filename = ""
        
        self.state = state
        
    def __del__(self) -> None:
        """Ensure we destroy the tempfile on exit"""
        self.__del_temp()
        
    def __del_temp(self) -> None:
        """Delete Temporary Directories
        
        Normally the context manager is sufficient but this
        doesn't work with streamlit. Therefore residing with
        this workaround.
        """
        try:
            shutil.rmtree(self.temp_file)
        except AttributeError:
            pass
        
        return
    
    def __error(self, placeholder, error_msg: str) -> None:
        """Helper functione to insert a given error message."""
        
        placeholder.error(error_msg)
        sleep(2)
        placeholder.empty()
        
        return
    
    def __display_progression(self, info: Dict[str, str]) -> None:
        """Display Download Progression"""
        self.ytdl_filename = info['filename']
        self.progress_placeholder.progress(
            int((info['downloaded_bytes']/info['total_bytes'])*100)
        )
    
    @st.cache(suppress_st_warning=True)
    def _create_download_button(self, video_name, video_content):
        """Create a Download button for a video+audio file."""
        st.download_button(
            label = "Video Content",
            data = video_content,
            file_name = f"{video_name}.mp4",
            mime = 'application/octet-stream'
        )
        return
    
    # Can't cache since we need to write onto disk...
    # simply remove the temp file when the object has been closed:
    # perhaps cache the object so it doesnt get destroyed instantly?
    # and refer to the object by a hash!
    
    # @st.cache(suppress_st_warning=True, ttl=1800)
    def download_video(self, video_name):
        """Download the provided video with ytdl."""
        # Set YDDL options appropiately
        ydl_opts = {
            # "format": f"bestvideo[ext={media_type.split('/')[-1]}]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            # "merge-output-format": f"{media_type.split('/')[-1]}",
            'outtmpl': f"",
            'verbose': True,
            'progress_hooks': [self.__display_progression]
        }

        # According to the youtube-dl docs
        ydl_opts['outtmpl'] = f"{location}/%(title)s.%(ext)s"

        # Download the requested video
        with ytdl.YoutubeDL(ydl_opts) as y_dl:
            
            if ydl_opts['outtmpl']:
                y_dl.download([url])
                
        self.ytdl_filename = self.__process_path(self.ytdl_filename)
        
        return True
    
    def write(self):
        """Write content to a page."""