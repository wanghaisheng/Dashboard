'''A default page with common functionalities.
It uses an abstract method to make debugging easier.
Created on: 23/10/21
Created by: @Blastorios'''

from abc import ABCMeta, abstractmethod
from pathlib import Path
from time import sleep

import streamlit as st

# Enforce common methods
class DefaultPageFormat(ABCMeta):
    
    @abstractmethod
    def _error(self):
        ...
    
    @abstractmethod
    def _generate_columns(self):
        ...
    
    @abstractmethod
    def write(self):
        ...


# Add basic functionalities here
class DefaultPage(metaclass=DefaultPageFormat):
    """A simple page with some basic functions."""
    
    def __init__(self):
        self.cwd = Path().cwd()
    
    def _error(self, placeholder, error_msg: str) -> None:
        """Helper functione to insert a given error message."""
        
        placeholder.error(error_msg)
        sleep(2)
        placeholder.empty()
        
        return
    
    def _generate_columns(self, column_number: int = 2):
        """Generate n streamlit columns"""
        return st.columns(column_number)