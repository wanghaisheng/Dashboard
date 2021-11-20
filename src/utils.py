from streamlit import markdown

from psutil import virtual_memory

def check_memory():
    mem = virtual_memory()
    return mem.percent

def add_custom_css(css: str = ""):
    markdown(
        f"""
        <style>
        {css}
        </style>
        """,
        unsafe_allow_html=True
    )