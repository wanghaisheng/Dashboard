'''Generic Tracker Construct to manage a temporary download folder.'''

from abc import ABCMeta, abstractmethod
from pathlib import Path
from shutil import rmtree
from typing import Optional

class IsTracked(ABCMeta):
    """
    Metaclass to use for modules that require tracking through
    the DownloadTracker object. This will ensure we have a smooth
    bridge by which we can debug the code if we miss certain
    methods or attributes.
    """
    
    @property
    @abstractmethod
    def reference(self):
        ...


class DownloadTracker:
    """
    DownloadTracker, responsible for updating and managing
    a download folder.
    """

    def __init__(self, temp_dir_name: Path, 
                 base_location: Path = Path(".").cwd(), 
                 max_folder_size: int = 15) -> object:
        self.temp_directory: Path = base_location / temp_dir_name
        self.max_folder_size: int = (1024 * 1024 * 1024) * max_folder_size
        self.store: tuple = ()
        self.quick_store: tuple = ()
        self.temp_access: object = None
        
        # Create the temp directory.
        self.temp_directory.mkdir(exist_ok = True)
        
    def __del__(self) -> None:
        self._del_temp_dir()
        
        return
    
    def _del_temp_dir(self) -> None:
        """Delete the temporary directory."""
        rmtree(self.temp_directory)
        
        return
    
    def _check_folder_size(self) -> bool:
        """Check if the folder size is greater than the
        maximum allowed size."""
        
        return self.temp_directory.stat().st_size > self.max_folder_size
    
    def is_in_store(self, item_name: str) -> bool:
        """Check if the item is in the tracker."""
        if item_name.isnumeric(): 
            return item_name in self.quick_store
        _hashed = str(hash(item_name))
        if len(_hashed) < 9: return False
        
        return _hashed[:9] in self.quick_store
    
    def get_item(self, item: object) -> Optional[object]:
        """Get the item from the tracker."""
        if not self.temp_access == item:
            self.temp_access = self.store[
                self.quick_store.index(item.reference)]
        
        _location = Path(self.temp_directory / item.reference)
        if _location.exists(): return self.temp_access
        
        return

    def add_item(self, item: object) -> None:
        """Append a new item to the tracker."""
        if self._check_folder_size(): self.del_item()
            
        if not self.is_in_store(item):
            self.store += (item,)
            self.quick_store += (item.reference,)
            
        return
    
    def del_item(self, reset_temp: bool = True) -> None:
        """Delete the first item from tracker. This will
        automatically invoke the `del` thundermethod from
        the stored VideoDownloader object and remove its 
        folder from the disk."""
        if reset_temp: self.temp_access = None
        self.store = self.store[1:]
        self.quick_store = self.quick_store[1:]
        
        return