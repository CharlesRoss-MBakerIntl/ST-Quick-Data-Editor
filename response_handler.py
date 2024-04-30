import requests
import streamlit as st

from data import Sources


def filter_package(package):
    
    filtered_package = []

    for item in package:
        cleaned_attributes = {key.strip(): value.strip() for key, value in item['attributes'].items() if value.strip() != '\xa0'}
        cleaned_item_package.append({'attributes': cleaned_attributes})

    return filtered_package





def submit_updates(package, token):

    #Create Dict
    update_list = {
        'Polygons': Sources().polygons,
        'Points': Sources().points,
        'Starts': Sources().starts,
        'Ends': Sources().ends
    }

    #Cycle through All Services to Update
    for service, service_url in update_list.items():
        
        #Set Update URL
        url = f"{service_url}/0/applyEdits"

        #Set Update Params
        params = {
            'f':'json',
            'token':token,
            'updates':f'{package}'
        }

        #Send Update Request
        try:
            response = requests.post(url, params=params)

            #If Connection Successful
            if response.status_code == 200:
            
                #Grab Result from Response
                try:
                    result = response.json()

                    #Check if Update Results in results and if success in content
                    if 'updateResults' in result and 'success' in result['updateResults'][0]:

                            #Update Successful
                            if result['updateResults'][0]['success'] == True:
                                st.success(f"{service} Updated")
                            
                            #If Success was a failure, report the error
                            elif result['updateResults'][0]['success'] == False:
                                st.error(f"Error Updating {service}: Failed to Connect")

                    
                    #If Update Results or Success Not in Results Package
                    else:
                        st.error(f"Error Updating {service}: Success Not in Results Package")

                #Response did not contain a JSON item, report error        
                except:
                    st.error(f"Error Updating {service}: Response Did Not Return JSON Package")
                    st.error(response.content)

            #Connection to AGOL failed, report error
            else:
                st.error(f"Error Updating {service}: Request Did Not Connect to AGOL")
                st.write(response.content)
            
        except Exception as e:
            st.error(f"Error Updating {service} <br> {e}")


        
        
