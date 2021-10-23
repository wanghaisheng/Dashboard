'''A default page with common functionalities.
It uses an abstract method to make debugging easier.
Created on: 23/10/21
Created by: @Blastorios'''

from abc import ABC, abstractmethod
from pathlib import Path

import streamlit as st

# Enforce common methods
class DefaultPageFormat(ABC):
    
    @abstractmethod
    def __error():
        pass
    
    @abstractmethod
    def __generate_columns():
        pass
    
    @abstractmethod
    def write():
        pass


# Add basic functionalities here
class DefaultPage(object, metaclass=DefaultPageFormat):
    """A simple page with some basic functions."""
    
    def __init__(self):
        self.cwd = Path().cwd()
    
     def __error(self, placeholder, error_msg: str) -> None:
        """Helper functione to insert a given error message."""
        
        placeholder.error(error_msg)
        sleep(2)
        placeholder.empty()
        
        return
    
    def __generate_columns(self, column_number: int = 2):
        """Generate n streamlit columns"""
        return st.beta_columns(column_number)