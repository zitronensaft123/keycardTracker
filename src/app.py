import streamlit as st
import matplotlib.pyplot as pyplot
import pandas as pd
import time

import api as api
import utils as utils
import db as db
import ui as ui
import login 

utils.removePageBar()

db.initDB()

if "currentPage" not in st.session_state:
    st.session_state.currentPage = "mainPage"

st.set_page_config(
    page_title="EFT KeycardTracker",
    page_icon="../assets/marin.jpg",
    layout="wide",
    menu_items=None,
    initial_sidebar_state="collapsed"
)

# remove random ass whitespace at top
st.markdown(utils.removeTopBar, unsafe_allow_html=True)

def showMain():
    statDict = utils.getStats()

    df_items = db.df_getItems()
    df_raids = db.df_getRaids()
    df_netWorth = db.df_getNetWorth()
    df_foundItems = utils.df_sumFoundItems()

    hcol1, spacer, hcol2 = st.columns([9,10,1], gap="medium")
    with hcol1:
        st.title("EFT KeycardTracker")

    with hcol2:
        if st.button("Login", key="loginButton"):
            st.session_state.currentPage = "loginPage"
            st.rerun()

    overall, keycard, addRaid, devOptions = st.tabs(["Overall","Keycard", "Add Raid", "Dev Settings"], width=1400)

    with overall:
        ui.overallTab()

    with keycard:
        ui.keycardTab()
    with addRaid:
        ui.addRaidTab()
            
    with devOptions:
        ui.devOptionsTab()

if st.session_state.currentPage == "mainPage":
    showMain()

if st.session_state.currentPage == "loginPage":
    login.showLogin()
