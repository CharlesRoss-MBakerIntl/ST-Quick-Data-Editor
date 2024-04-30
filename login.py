from agol_restapi import token_generation
import streamlit as st


def login_form():
    
    empty_login = st.empty()

    with empty_login.form("Login Form"):

        css="""
        <style>
            [data-testid="stForm"] {
                background: white;
            }
        </style>
        """


        st.write(css, unsafe_allow_html=True)
        

        username = st.text_input("Username")
        password = st.text_input("Password",type='password')

        login_button = st.form_submit_button("Login")

        if login_button:
            
            try:
                token  = token_generation(username, password)

                if token != None:
                    st.session_state['token'] = token

                st.session_state['logged_in'] = True
                
                return True

            
            except Exception as e:
                st.error(f"{e}: Check your username and password")
        

        return False