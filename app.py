import streamlit as st
import matplotlib
import pandas as pd

import api
import main
import utils
import db

st.set_page_config(
    page_title="EFT KeycardTracker",
    page_icon="marin.jpg",
    layout="wide",
    menu_items=None
)

# remove random ass whitespace at top
st.markdown(utils.removeTopBar, unsafe_allow_html=True)

st.title("EFT KeycardTracker")

stats, addRaid, devOptions = st.tabs(["Statistics", "Add Raid", "Dev Settings"], width=600)

with stats:
    st.write("print stats here")

    col1, col2 = st.columns(3)

    with col1:
        st.caption("Overall:")
        
with addRaid:
    st.write("addRaid logic here")

with devOptions:
    st.caption("this will bypass 10 Minute Delay! Use with Caution")
    if st.button("fetch Data"):
        st.write("asd")

