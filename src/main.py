'''Streamlit Dashboard for Common Services
Created on: 23/10/21
Created by: @Blastorios'''

import streamlit as st

from utils import add_custom_css
from pages import STARTING_PAGE, PAGE_MAP

st.set_page_config(
    page_title = 'Blastorios Dashboard',
    # page_icon = favicon,
    layout = 'wide',
    initial_sidebar_state = 'auto')

# Whenever I want to update the css:
add_custom_css(
    
)

# Setup the sidebar:
st.sidebar.title("Services")

radio_selection = PAGE_MAP.copy()
radio_selection.pop(STARTING_PAGE, None)

# Ensure we always have the 'welcomepage' on top of the service list.
current_page = st.sidebar.radio("", [STARTING_PAGE] + sorted(list(radio_selection)))

st.sidebar.info(
    """
    Dashboard by [Blastorios](https://github.com/Blastorios)
    
    All is free to use, services that require a password: `root(16) + 16^2 = ?`
    
    Chat with me on [discord](https://discord.gg/nZYQsC6fHX)!
    """)

# Welcome Page:
def main():
    PAGE_MAP[current_page]().write()
    

if __name__ == "__main__":
    main()
