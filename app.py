import streamlit as st
import matplotlib.pyplot as pyplot
import pandas as pd

import api
import utils
import db

db.initDB()

st.set_page_config(
    page_title="EFT KeycardTracker",
    page_icon="marin.jpg",
    layout="wide",
    menu_items=None
)

# remove random ass whitespace at top
st.markdown(utils.removeTopBar, unsafe_allow_html=True)

def newline():
    st.write("")

statDict = utils.getStats()

df_items = db.df_getItems()
df_raids = db.df_getRaids()
df_netWorth = db.df_getNetWorth()
df_foundItems = utils.df_sumFoundItems()

st.title("EFT KeycardTracker")

overall, keycard, addRaid, devOptions = st.tabs(["Overall","Keycard", "Add Raid", "Dev Settings"], width=1400)

with overall:

    newline()

    tcol1, tcol2, tcol3, tcol4, tcol5 = st.columns([1,1,1, 1, 1], gap="medium")

    accountStats = utils.getTarkovTrackerStats()

    with tcol1:
        st.metric("Account Name:", accountStats["account"]["name"])
    with tcol2:
        st.metric("Account Level:", accountStats["account"]["level"])
    with tcol3:
        st.metric("Faction:", accountStats["account"]["faction"])
    with tcol4:
        st.metric("Gamemode:", accountStats["account"]["mode"])
    st.write("-------------------------")

    st.write("")

    mcol1, mcol2, mcol3 = st.columns([2, 3, 4], gap="medium")

    with mcol1:
        new_balance = st.text_input("Update Balance")

        if new_balance:
            try:
                db.addNetWorthEntry(int(new_balance))
                st.cache_data.clear() 
            except ValueError:
                st.error("Please enter a valid integer")
        
        statDict = utils.getStats()

        st.metric(
            "Current RUB", 
            utils.formatNumber(statDict["overall"]["currentMoney"], 1), 
            (utils.formatNumber(statDict["overall"]["currentMoney"] - statDict["overall"]["previousMoney"], 1))
        )
        st.metric("Highest ever recorded:", utils.formatNumber(statDict["overall"]["maxMoney"], 1))
        st.metric("Lowest ever recorded:", utils.formatNumber(statDict["overall"]["minMoney"], 1))

    with mcol2:
        df_netWorth = db.df_getNetWorth()
        st.line_chart(df_netWorth, x="entryID", y="money", x_label="Balance", y_label="Entry")
    with mcol3:
        st.write("sigma")

    st.write("-------------------------")
    st.write("")

    bcol1, bcol2, bcol3 = st.columns([1,1,1], gap="medium")

    with bcol1:
        st.metric("Kappa Progress:", accountStats["quests"]["kappa"] + " / 255")
    with bcol2:
        st.metric("Lightkeeper Progress:", accountStats["quests"]["lightkeeper"] + " / 100")
    with bcol3:
        st.metric("Overall Quest Progress:", accountStats["quests"]["overall"] + " / 469")

with keycard:
    keycardStats = utils.getStats()
    tcol1, tcol2, tcol3 = st.columns([1,1,1], gap="medium")

    with tcol1:
        st.metric("Profit from Black Keycards:", utils.formatNumber(keycardStats["keycard"]["revenue"], 1)) 
    with tcol2:
        st.metric("Money spent:", utils.formatNumber(keycardStats["keycard"]["moneySpent"], 1))
    with tcol3:
        st.metric("Raw Money earned", utils.formatNumber(keycardStats["keycard"]["moneyEarned"], 1))  

    mcol1, mcol2, mcol3 = st.columns([1,1,1], gap="medium")

    with mcol1:
        st.metric("Total Blackcard Raids:", utils.formatNumber(keycardStats["keycard"]["totalRaids"], 0))
    with mcol2:
        st.metric("Best Raid (RUB):", utils.formatNumber(keycardStats["keycard"]["bestRaid"], 1))
    with mcol3:
        st.metric("worst Raid (RUB):", utils.formatNumber(keycardStats["keycard"]["totalRaids"], 1))


with addRaid:
    items = db.df_getItemsTable()

    foundItems = {}

    
    selection = st.selectbox(label=f" Select an Item you found ({db.getFetchedItems()})", options=items["name"])
    newline()
    if "foundItems" not in st.session_state:
        st.session_state.foundItems = {}

    tcol1, tcol2, spacer = st.columns([1,1, 3], gap="medium")

    with tcol1:
        if st.button(f"+  Add {selection}"):
            if selection in st.session_state.foundItems:                
                st.session_state.foundItems[selection] += 1
            else:
                st.session_state.foundItems[selection] = 1

    with tcol2:
        if st.button("X Clear Selection"):
            st.session_state.foundItems.clear()
    
    st.write(st.session_state.foundItems)

with devOptions:
    st.caption("this will bypass 10 Minute Delay! Use with Caution")
    if st.button("fetch Data"):
        db.updatePrices(1)
        st.cache_data.clear()
        st.rerun()
        st.write(f"Fetched {db.getFetchedItems()} Items")

