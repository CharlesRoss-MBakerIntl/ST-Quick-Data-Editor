import requests
import pytz
import pandas as pd
import numpy as np
import streamlit as st

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

########## TOKEN GENERATION ########

def token_generation(username, password):
    
    #Rest Api Token URl
    url = 'https://www.arcgis.com/sharing/rest/generateToken'

    #User Data to Generate Token
    data = {
        "username":username,
        'password':password,
        'referer':'https://www.arcgis.com'
    }

    #Additional Parameters
    params = {
        'f':'json'
    }

    #Send Response to Generate Token
    response = requests.post(url, params=params, data=data)

    st.write(response)
    st.write(response.json())

    #Save Token
    try:
        token = response.json()["token"]
        return token

    except:
        raise Exception("Failed to Load Token")




########## AGOL TABLE TO PANDAS DATAFRAME ###########

def agol_table_to_pd(service_url, layer, token, convert_dates = "n", drop_objectids = "n"):

    url = f'{service_url}/{str(layer)}/query'

    #Enter Serach Parameters to Pull Data Table
    params = {
        'f': 'json',
        'token': token,
        'where': '1=1',  
        'outFields': '*',
        'returnGeometry': False
    }

    #Send Repsonse to Pull Table
    response = requests.get(url, params=params)

    #If Response Connection Successful, Pull Data and Convert to Pandas Dataframe
    if response.status_code == 200:
        data = response.json()
        table = data.get('features', [])
        df = pd.DataFrame([row['attributes'] for row in table])



    #Drop ObjectID
    if drop_objectids.lower() == "y":
    
        if "ObjectId" in df.columns:
            df = df.drop(columns = "ObjectId")

        elif "objectid" in df.columns:
            df = df.drop(columns = "objectid")

        elif "OBJECTID" in df.columns:
            df = df.drop(columns = "OBJECTID")

        elif "Fid" in df.columns:
            df = df.drop(columns = "Fid")

        elif "fid" in df.columns:
            df = df.drop(columns = "fid")

        elif "FID" in df.columns:
            df = df.drop(columns = "FID")


    #Catch All Date Fields and Convert to Pandas Datetime if Selected
    if convert_dates.lower() == "y":
        agol_date_convert_akt(data, df)
    
    elif convert_dates.lower() == "n":
        pass

    else:
        pass


    #Fill NAs or Nans
    df.fillna("", inplace = True)
    

    return df





######## AGOL SPATIAL GEOMETRY PULL (POLYGONS) ##########
def pull_coordinates(service_url, layer, token, uid, fields):
    
    # Set Service URL
    url = f'{service_url}/{str(layer)}/query'

    #Enter Serach Parameters to Pull Geometry
    params = {
        'f': 'json',
        'token': token,
        'where': f"UID='{uid}'",  
        'outFields': fields,
        'outSR': '4326',
        'returnGeometry': True
    }

    #Send Repsonse to Pull Table
    response = requests.get(url, params=params)

    
    #If Response Connection Successful, Pull Data and Convert to Pandas Dataframe
    if response.status_code == 200:
        data = response.json()

        converted = []

        geometries = data['features'][0]['geometry']['rings']

        for geometry in geometries:

            geometry = np.array(geometry)
            coordinates = np.flip(geometry, axis = -1).tolist()

            converted.append(coordinates)

    return converted




def pull_geometry(service_url, layer, token, uid, fields):
    
    # Set Service URL
    url = f'{service_url}/{str(layer)}/query'

    #Enter Serach Parameters to Pull Geometry
    params = {
        'f': 'json',
        'token': token,
        'where': f"UID='{uid}'",  
        'outFields': fields,
        'outSR': '4326',
        'returnGeometry': True
    }

    #Send Repsonse to Pull Table
    response = requests.get(url, params=params)


    #If Response Connection Successful, Pull Data and Convert to Pandas Dataframe
    if response.status_code == 200:
        data = response.json()
        objectid = data['features'][0]['attributes']['OBJECTID']
        geometry = data['features'][0]['geometry']['rings']

    return objectid, geometry



######## AGOL SPATIAL GEOMETRY PULL (POINTS) ##########
def pull_point(service_url, layer, token, uid):
    
    coordinates = {}

    # Set Service URL
    url = f'{service_url}/{str(0)}/query'

    #Enter Serach Parameters to Pull Geometry
    params = {
        'f': 'json',
        'token': token,
        'where': f"UID='{uid}'",  
        'outFields': 'UID',
        'outSR': '4326',
        'returnGeometry': True
    }

    #Send Repsonse to Pull Table
    response = requests.get(url, params=params)

    #If Response Connection Successful, Pull Data and Convert to Pandas Dataframe
    if response.status_code == 200:
        data = response.json()
        
        if 'features' in data and len(data['features']) == 1 and 'geometry' in data['features'][0]:
            
            geometry = data['features'][0]['geometry']

            if 'x' in geometry and 'y' in geometry:
                
                coordinates['x'] = round(geometry['x'], 12)
                coordinates['y'] = round(geometry['y'], 12)


    return coordinates







######## AGOL TABLE DATE CONVERT ##########

def agol_date_convert_akt(agol_data, agol_df):

    #Set Alaska Timezone
    alaska_tz = pytz.timezone('US/Alaska')
    
    #Pull Fields from AGOL Data Table, BEFORE PD CONVERSION
    if agol_data.get("fields") != None:
        fields = agol_data['fields']

        #Find Field Names and Types
        field_types = pd.DataFrame([[row['name'], row['type']] for row in fields], columns = ['name', 'type'])

        #Iterate Through Data Field, if Field is an ESRIDATETYPE, Check if Field in AGOL DF, If There, Convert to Datetime
        for index,row in field_types.iterrows():
            if row['type'] == 'esriFieldTypeDate':
                date_field = row['name']
                if date_field in agol_df.columns:
                    agol_df[date_field] = pd.to_datetime(agol_df[date_field], unit='ms')
                    agol_df[date_field] =  agol_df[date_field].dt.tz_localize('UTC').dt.tz_convert(alaska_tz)
                    agol_df[date_field] = agol_df[date_field].apply(lambda x: x.strftime('%B %d, %Y   %H:%S'))

        return agol_df

    elif agol_data.get("fields") == None:
        raise Exception("Input Data Table Has No 'Fields' Attribute")
    





######## PULL THE OBJECTID FROM FEATURE LAYER #############

# Function to get OBJECTID for a given UID in a feature layer
def pull_objectid(service_url, layer, uid, token):
    
    #Set Search Params
    params = {
        'where': f"UID = '{uid}'",
        'outFields': 'OBJECTID',
        'f': 'json',
        'token': token,
        'returnGeometry': False
    }

    #Submit Request
    response = requests.get(f"{service_url}/{str(layer)}/query", params=params)

    # Store Data
    data = response.json()

    #Check for Features within Data
    if 'features' in data and data['features']:

        #Grab OBJECTID
        return data['features'][0]['attributes']['OBJECTID']
    
    else:
        return None
    





def package_update(survey_url, layer, token, payload):
    """
    Takes a prepared data payload and feature layer information and sends updates through a AGOL REST API request
    to update the "Weekly_Update_Status" field.

    If an error occurs within the connection or update process, the function will return an error log, if no error occurs,
    fucntion returns None.
    """
        
    #Set the Error Catch
    error = None
    
    try:

        #ApplyEdits URL for Survey Table
        url = f'{survey_url}/{layer}/applyEdits'

        #Create Upload Parameters
        params = {
            'f':'json',
            'token':token,
            'updates':f'{payload}'
        }

        #Initiate Update to AGOL
        response = requests.post(url, params)


        #If Response Connected
        if response.status_code == 200:

            #Create JSON Dict from Response
            response = response.json()

            #If Response Update was NOT Successfull, Create Error Log
            if response['updateResults'][0]['success'] == False:

                error = {   'Event':'Uploading Status Update Failed',
                            'OBJID': response['updateResults'][0]['uniqueId'],
                            'Code': response['updateResults'][0]['error']['code'],
                            'Details': response['updateResults'][0]['error']['description']}
                
                raise Exception(f"Failed to Upload Status to AGOL")

        
        #If there is a failure to connect
        elif response.status_code == 400:

            error = {   'Event': 'Failed to Connect',
                        'OBJID': '',
                        'Code': response['error']['code'],
                        'Details': response['error']['details'] }
            
            raise Exception("Failed to Connect to AGOL")
            

        #If Response Didn't Connect, Raise Exception
        else:
            error = {   'Event': 'Failed to Connect',
                        'OBJID': '',
                        'Code':'',
                        'Details': '' }
            
            raise Exception("Failed to Connect to AGOL")


    #If Exception Occurred, Return Error
    except Exception as e:
            
        return error