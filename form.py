import streamlit as st
import leaflet
import folium

from streamlit_folium import st_folium
from streamlit_folium import folium_static

from agol_restapi import agol_table_to_pd
from agol_restapi import pull_coordinates

from response_handler import submit_updates
from response_handler import chunk_dictionary
from data import Sources



def project_select(token):
    
    data = Sources().polygons
    df = agol_table_to_pd(data, 0, token)

    selection = st.selectbox("Select a Project", df["Public_Proj_Name"], index = None, placeholder = "Select your project from the dropdown list")

    if selection != None:

        # Select the Project Row from the DataFrame and Store Project in Session State
        project = df[df['Public_Proj_Name'] == selection]
        st.session_state['project'] = project


        # Save UID for Project and Store in Session State
        uid = project['UID'].iloc[0]
        st.session_state['uid'] = uid


        # Save UID for Project and Store in Session State
        objectid = project['OBJECTID'].iloc[0]
        st.session_state['OBJECTID'] = uid


        #Grab the Coordiantes for the Project Polygon and Store in Session State
        coordinates = pull_coordinates(data, 0, token, uid, [])
        st.session_state['coordinates'] = coordinates

        return True


def proj_map(coordinates, proj_name):

    #Produce Map of Project
    project_map = folium.Map(location=coordinates[0][0], zoom_start=12, zoom_control=False, dragging = False, scrollWheelZoom=False)
    folium.Polygon(locations=coordinates, color='blue', fill=True, fill_opacity=0.4, popup = proj_name).add_to(project_map)
    project_map.fit_bounds(project_map.get_bounds())

    #Display Map on Form
    st_folium_map = folium_static(project_map, width = 670, height = 400)




def edit_form(project, coordinates, project_name, token):

    #Create Empty Form
    info_form = st.empty()

    #Create Form
    with info_form.form("Edit Form"):

        proj_map(coordinates, project_name)
    
        #First Section
        public_name = st.text_input("Public Project Name", key = 'public_proj_name', value = project['Public_Proj_Name'].iloc[0])

        #Second Section
        tech_name = st.text_input("Technical Project Name", key = 'proj_name', value = project['Proj_Name'].iloc[0])

        #Third Section
        col1, col2, col3 = st.columns(3)
        with col1:
            iris = st.text_input("IRIS Number", key = 'iris', value = project['IRIS'].iloc[0])
        with col2:
            stip = st.text_input("STIP ID", key = 'stip', value = project['STIP'].iloc[0])
        with col3:
            fed_num = st.text_input("Federal Project Number", key = 'fed_num', value = project['Fed_Proj_Num'].iloc[0])


        st.write("#")

        #Fourth Section
        col4, col5 = st.columns(2)
        with col4:
            proj_prac = st.text_input("Project Practice", key = 'proj_prac', value = project['Proj_Practice'].iloc[0])
        with col5:
            new_continue = st.text_input("New or Continuing?", key = 'new_continue', value = project['New_Continuing'].iloc[0])

        # Fifth Row Project Start/End Date
        col6, col7 = st.columns(2)
        with col6:
            antic_start = st.text_input("Anticipated Start Date (MM-YYYY)", key = 'antic_start', value = project['Anticipated_Start'].iloc[0])
        with col7:
            antic_end = st.text_input("Anticipated End Date (MM-YYYY)", key = 'antic_end', value = project['Anticipated_End'].iloc[0])


        # Fifteenth Row Additional Project Info
        col8, col9 = st.columns(2)
        with col8:
            contract_amount = st.text_input("Contract Amount (For Awarded Projects)", key = 'contract_amount', value = project['Contract_Amount'].iloc[0])
        with col9:
            fund_type = st.text_input("Funding Type", key = 'fund_type', value = project['Fund_Type'].iloc[0])


        st.write("#")

        #Eigth Section
        impact_comm = st.text_input("Impacted Communities", key = 'impacted_communities', value = project['Impacted_Communities'].iloc[0])


        #Seventh Section
        col14, col15 = st.columns(2)
        with col14:
            route_id = st.text_input("Route ID", key = 'route_id', value = project['Route_ID'].iloc[0])
        with col15:
            route_name = st.text_input("Route Name", key = 'route_name', value = project['Route_Name'].iloc[0])
            
        
        st.write("#")

        #Eighth Row Design Manager
        col16, col17, col18 = st.columns(3)
        
        with col16:
            dm = st.text_input("Design Manager", key = 'dm', value = project['Des_Mang_Name'].iloc[0])
        with col17:
            dmp = st.text_input("Phone", key = 'dmp', value = project['Des_Mang_Phone'].iloc[0])
        with col18:
            dme = st.text_input("Email", key = 'dme', value = project['Des_Mang_Email'].iloc[0])


        # Ninth Row Construction Manager
        col19, col20, col21 = st.columns(3)
        
        with col19:
            cm = st.text_input("Construction Manager", key = "cm", value = project['Con_Mang_Name'].iloc[0])
        with col20:
            cmp = st.text_input("Phone", key = "cmp", value = project['Con_Mang_Phone'].iloc[0])
        with col21:
            cme = st.text_input("Email", key = 'cme', value = project['Con_Mang_Email'].iloc[0])


        # Tenth Row Project Engineer
        col22, col23, col24 = st.columns(3)
        
        with col22:
            pe = st.text_input("Project Engineer", key = 'pe', value = project['Proj_Eng_Name'].iloc[0])
        with col23:
            pep = st.text_input("Phone", key = 'pep', value = project['Proj_Eng_Phone'].iloc[0])
        with col24:
            pee = st.text_input("Email", key = 'pee', value = project['Proj_Eng_Email'].iloc[0])


        # Tenth Row Project Engineer
        col25, col26 = st.columns(2)
        
        with col25:
            scn = st.text_input("Survey Contact Name", key = 'scn', value = project['Survey_Contact_Name'].iloc[0])
        with col26:
            sce = st.text_input("Survey Contact Email", key = 'sce', value = project['Survey_Contact_Email'].iloc[0])
        

        st.write("#")

        #  Section 
        proj_desc = st.text_area("Project Description", height=200, max_chars=5000, value = project['Proj_Desc'].iloc[0])

        proj_purp = st.text_area("Project Purpose", height=200, max_chars=5000, value = project['Proj_Purp'].iloc[0])

        proj_impact = st.text_area("Curent Project Impact", height=200, max_chars=5000, value = project['Proj_Impact'].iloc[0])

        proj_web = st.text_input("Project Website", key = 'proj_web', value = project['Proj_Web'].iloc[0])
        
        apex_link = st.text_input("APEX Mapper Link", key = 'apex_link', value = '')

        st.write("#")

        # Tenth Row Project Engineer
        col25, col26 = st.columns(2)
        
        with col25:
            scale_map_series = st.number_input("Scale Map Series", key = 'scale_map', value = project['Scale_Map_Series'].iloc[0])
        with col26:
            scale = st.number_input("Scale", key = 'scale', value = project['Scale'].iloc[0])



        #Create Dicitionary from All Fields
        package = {
                    'Public_Proj_Name': public_name,
                    "Proj_Name": tech_name,
                    "IRIS":iris,
                    "Fed_Proj_Num":fed_num,
                    "STIP":stip,
                    "Route_ID": route_id,
                    "Route_Name": route_name,
                    "Impacted_Communities":impact_comm,
                    "Proj_Desc":proj_desc,
                    "Proj_Purp": proj_purp,
                    "Proj_Impact":proj_impact,
                    "Proj_Web":proj_web,
                    "Des_Mang_Name":dm,
                    "Des_Mang_Email":dme,
                    "Des_Mang_Phone":dmp,
                    "Con_Mang_Name":cm,
                    "Con_Mang_Email":cme,
                    "Con_Mang_Phone":cmp,
                    "Proj_Eng_Name":pe,
                    "Proj_Eng_Email":pee,
                    "Proj_Eng_Phone":pep,
                    "Survey_Contact_Name":scn,
                    "Survey_Contact_Email":sce,
                    "Contract_Amount":contract_amount,
                    "Anticipated_Start":antic_start,
                    "Anticipated_End":antic_end,
                    "Proj_Practice":proj_prac,
                    "Fund_Type":fund_type,
                    "New_Continuing":new_continue,
                    "APEX_Mapper_Link":apex_link,
                    "Scale_Map_Series": scale_map_series,
                    "Scale": scale,

                    }


        #Chunk Packaged Data for Download
        chunks = chunk_dictionary(package, project['OBJECTID'].iloc[0], 3)


        st.write("")
        st.write("")

        # Add a submit button
        submit_button = st.form_submit_button("Submit Edits")


    if submit_button:
        pass
        submit_updates(chunks, token)

        