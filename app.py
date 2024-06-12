import streamlit as st
from login import login_form
from form import project_select
from form import proj_map
from form import edit_form

from agol_restapi import token_generation

token = token_generation("AKDOT_APEX", "@KD0T_@p3x")

st.session_state['project'] = None

#Select Project
sel_project = project_select(token)


if sel_project == True:
    
    #Pull Project Name
    project = st.session_state['project']

    #Pull Project Coordinates
    coordinates = st.session_state['coordinates']
    
    #Display Project Edit Form
    edit_form(project, coordinates, project['Public_Proj_Name'].iloc[0], token)

    
