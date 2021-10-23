'''Streamlit Dashboard for Common Services
Created on: 23/10/21
Created by: @Blastorios'''

import streamlit as st

from utils import add_custom_css
from pages import PAGE_MAP

st.set_page_config(
    page_title='Blastorios Dashboard',
    # page_icon = favicon,
    layout='wide',
    initial_sidebar_state='auto')

add_custom_css()

st.sidebar.title("Services:")

current_page = st.sidebar.radio("", sorted(list(PAGE_MAP)))

st.sidebar.info(
    """
    Official GameBois Services
    
    All is free to use
    
    Chat with us on [discord](https://discord.gg/nZYQsC6fHX)!
    """)

# Welcome Page
def main():
    PAGE_MAP[current_page].write()
    

if __name__ == "__main__":
    main()