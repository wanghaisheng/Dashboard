'''Simple Welcome Page
Created on: 23/10/21
Created by: @Blastorios'''

import uuid

import streamlit as st

from .default import DefaultPage

class WelcomePage(DefaultPage):
    """We need to welcome people ofc :)"""
    
    def __init__(self):
        super().__init__()
        pass
    
    def login_form(self):
        # Create a login form here!
        return
    
    def write(self):
        """Construct the welcome page."""
        
        st.title("Welcome to Blastorios' Dashboard")
        
        st.markdown("""This started as a **small side project**
            but I found myself adding more pages that
            might be helpful to others :smile:.""")
        
        st.subheader("Persistance?")
        
        st.info("""Visit the website more often and would
                    like to have things readily available?
                    Simply **login** in the sidebar and I 
                    will remember your previous actions!""")
        
        # TODO: Insert Login Form
        
        st.subheader("New Utilities?")
        
        st.info("""Feel free to **open an issue on GitHub** if you
            would **like to see more apps/functions** added 
            (which might help others as well!).""")
        
        st.subheader("Important!")
        
        st.info("""Streamlit services are restarted on
            whenever you reload the page.
            Have a long running job? Leave
            the page open otherwise you will
            lose all progress.""")
    
        return
        