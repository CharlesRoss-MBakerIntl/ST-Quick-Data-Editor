import streamlit as st
from login import login_form
from form import project_select
from form import proj_map
from form import edit_form

#Checks if Token Already Generated, If Not, Asks for Login to Create One
if 'logged_in' not in st.session_state:
        
    login = login_form()
    
    if login == True:
        st.rerun()

else:
    
    #Generate Token
    token = st.session_state['token']
    
    #Select Project
    sel_project = project_select(token)

    #If Project Selected
    if 'project' in st.session_state:

        #Pull Project Name
        project = st.session_state['project']

        #Pull Project Coordinates
        coordinates = st.session_state['coordinates']

        #Project and Coordinates Exist
        if 'project' in st.session_state and 'coordinates' in st.session_state:
        
            st.write("#")

            #Display Project Edit Form
            edit_form(project, coordinates, project['Public_Proj_Name'].iloc[0], token)
