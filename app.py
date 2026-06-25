import streamlit as st
import matplotlib
import pandas as pd

import api
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

statDict = utils.getStats()

st.title("EFT KeycardTracker")

overall, keycard, addRaid, devOptions = st.tabs(["Overall","Statistics", "Add Raid", "Dev Settings"], width=600)

with overall:
    col1, col2 = st.columns(2)

    with col1:
        st.write(statDict["overall"]["currentMoney"])

with keycard:
    st.write("print stats here")
        
with addRaid:
    st.write("addRaid logic here")

with devOptions:
    st.caption("this will bypass 10 Minute Delay! Use with Caution")
    if st.button("fetch Data"):
        st.write("asd")

