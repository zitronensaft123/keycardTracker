import streamlit as st
import db
import bcrypt

def showLogin():
    if "authMode" not in st.session_state:
        st.session_state.authMode = "login"

    if st.session_state.authMode == "login":
        spacer, col2, spacer2 = st.columns([3,2,3])

        users = db.df_getUserTable()

        with col2:
            user = st.text_input("Username")
            password = st.text_input("Password")

            if user not in users["username"]:
                st.write("No Account with this Username found.")
                if st.button("Create new Account", key="createAccount"):
                    st.session_state.authMode == "register"
                    st.rerun()
            
            if db.checkPassword(user, password):
                st.write(f"Succesfully logged in as: {user}!")

                st.session_state.userID = users["username"]["userID"]
                st.session_state.loggedIn = True
                st.session_state.username = user
                
                st.session_state.currentPage = "mainPage"
                st.rerun()

    if st.session_state.authMode == "register":

        correctPin = st.secrets["REGISTER_PIN"]
        spacer, col2, spacer2 = st.columns([3,2,3])

        users = db.df_getUserTable()

        with col2:
            user = st.text_input("Username")
            password = st.text_input("Password")
            passwordConf = st.text_input("Confirm Password")
            pin = st.text_input("Pin")

            if st.button("Register", key="registerButton"):
                if pin != correctPin:
                    st.error("Pin wrong. Please try again")
                    st.rerun()
                if password != passwordConf:
                    st.error("Passwords dont match. Please try again")
                    st.rerun()
                if user in users["username"]:
                    st.error("Username already exists. Please try again")
                    st.rerun()
                db.addNewUser(user, password)
                st.write("User Added!")
                st.session_state.authMode = "login"
                st.rerun()