import streamlit as st
import matplotlib.pyplot as pyplot
import pandas as pd

import src.api as api
import src.utils as utils
import src.db as db
import time
import src.ui as ui

db.initDB()

st.set_page_config(
    page_title="EFT KeycardTracker",
    page_icon="assets/marin.jpg",
    layout="wide",
    menu_items=None
)

# remove random ass whitespace at top
st.markdown(utils.removeTopBar, unsafe_allow_html=True)

statDict = utils.getStats()

df_items = db.df_getItems()
df_raids = db.df_getRaids()
df_netWorth = db.df_getNetWorth()
df_foundItems = utils.df_sumFoundItems()

st.title("EFT KeycardTracker")

overall, keycard, addRaid, devOptions = st.tabs(["Overall","Keycard", "Add Raid", "Dev Settings"], width=1400)

with overall:
    ui.overallTab()

with keycard:
    ui.keycardTab()
with addRaid:
    ui.addRaidTab()
        
with devOptions:
    ui.devOptionsTab()

