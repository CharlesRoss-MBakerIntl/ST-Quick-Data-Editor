import requests
import json
import streamlit as st

from data import Sources


def chunk_dictionary(package, objectid, num_chunks):

    #Filter Package for \xao values
    for key, value in package.items():
        
        # Check if the value is a string
        if isinstance(value, str):
            
            # If the value contains '\xa0', strip it away
            if '\xa0' in value:
                package[key] = value.replace('\xa0', '').strip()
            
            # If the value only contains '\xa0', remove the entry entirely
            elif value.strip() == '\xa0':
                del package[key]
    
    # Calculate the size of each chunk
    chunk_size = len(package) // num_chunks
    remainder = len(package) % num_chunks

    # Initialize the list to store chunks
    chunks = []
    start_index = 0

    # Loop through the dictionary keys and create chunks
    for i in range(num_chunks):
        
        # Calculate the end index for the current chunk
        end_index = start_index + chunk_size + (1 if i < remainder else 0)
        
        # Extract keys for the current chunk
        chunk_keys = list(package.keys())[start_index:end_index]
        
        # Create a new chunk dictionary
        chunk = {key: package[key] for key in chunk_keys}

        # Add ObjectID to chunk
        chunk['OBJECTID'] = objectid
        
        # Add the chunk to the list
        chunks.append(chunk)
        
        # Update the start index for the next chunk
        start_index = end_index


    return chunks

    




def submit_updates(chunks, token):

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

        #Create Error Catch
        success = 0
        error = 0
        message = ""

        #Update Chunks of Data
        for chunk in chunks:

            if len(chunk) != 0:

                payload = [{'attributes':chunk}]

                #Set Update Params
                params = {
                    'f':'json',
                    'token':token,
                    'updates':f'{payload}'
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
                                        success += 1
                                    
                                    #If Success was a failure, report the error
                                    elif result['updateResults'][0]['success'] == False:
                                        error += 1
                                        message = f"Error Updating {service}: Failed to Connect"

                            
                            #If Update Results or Success Not in Results Package
                            else:
                                error += 1
                                message = f"Error Updating {service}: Success Not in Results Package"

                        #Response did not contain a JSON item, report error        
                        except:
                            error += 1
                            st.write(response.content)
                            message = f"Error Updating {service}: Response Did Not Return JSON Package"
            
                    #Connection to AGOL failed, report error
                    else:
                        error += 1
                        message = f"Error Updating {service}: Request Did Not Connect to AGOL"
    
                    
                except Exception as e:
                    error += 1
                    message = f"Error Updating {service} <br> {e}"



        #Display message from catches
        if error == len(chunks):
            st.error( f"{message}")

        elif error != len(chunks) and success >= 1:
            st.success(f"{service} Updated")      


        
        
