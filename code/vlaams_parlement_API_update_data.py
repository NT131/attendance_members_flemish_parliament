#!/usr/bin/env python
# coding: utf-8

# # Vlaamse parlement API

# Het Vlaamse Parlement stelt de data uit de parlementaire databank ook ter beschikking via een API: https://www.vlaamsparlement.be/nl/parlementair-werk/dossiers/dossiers/open-data en http://ws.vlpar.be/e/opendata/api/.

# # Setting up

# In[1]:


# show all outputs of cell, not merely of last line (i.e. default of Jupyter Notebook)
from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = "all"


# In[2]:


import numpy as np
import pandas as pd

import csv
import pickle

from collections import defaultdict

import requests

from datetime import datetime, timedelta
import locale # to allow date parsing for dates in Dutch

from collections import Counter

import matplotlib.pyplot as plt

import copy

import os


# In[3]:


# # Set the locale to Dutch
# locale.setlocale(locale.LC_ALL, 'nl_NL')


# In[4]:


# # Obtain string of current date
# today_str = datetime.now().strftime("%Y-%m-%d")
# today_str 


# In[5]:


# Set base_url of api
base_url = "https://ws.vlpar.be/e/opendata"


# In[6]:


# The webpage of the API shows some interesting fields:
# * `/stats/{commId}/{zj}`: statistieken voor commissie per zittingsjaar
# * `/vv/huidige`: Lijst van huidige Vlaamse volksvertegenwoordigers
# * `/vv/gewezen`: Lijst van gewezen Vlaamse volksvertegenwoordigers
# * `/vv/{persoonId}` Detailgegevens volksvertegenwoordiger
# * `/comm/huidige` Commissies van de huidige legislatuur
# * `/comm/{commId}` Samenstelling commissie
# * `/verg/vorige` Lijst van vorige vergaderingen voor periode
# * `/verg/zoek/datums` Lijst van vorige vergaderingen (beperkte data) binnen een zekere periode


# # Read in data

# In[7]:


def get_endpoint(endpoint: str):
    """
    Return data available at inserted endpoint
    """
    # Make the GET request
    response = requests.get(f"{base_url}{endpoint}")

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        data = response.json()  # Parse JSON response
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")

    return data


# ## Members and parties

# First we obtain the current members of parliament.

# In[8]:


volksvertegenwoordigers_json = get_endpoint("/vv/huidige")

# # Inspect data
# volksvertegenwoordigers_json

# Parse json into dataframe. Visual inspection showed data is stored in 'items' key
volksvertegenwoordigers_df = pd.DataFrame.from_dict(
    pd.json_normalize(volksvertegenwoordigers_json['items']), 
    orient='columns')


# In[9]:


# # Inspect results
# volksvertegenwoordigers_df.head()
# volksvertegenwoordigers_df.columns


# This dataframe contains the relevant party names and their corresponding colour. We can use this later when visualising, so we obtain this and store it.

# In[10]:


partij_kleur_dict = {} # Create empty dict to fill

# Iterate over each member and if its party and colour not yet in dict, include
for kleur, partij in zip(volksvertegenwoordigers_df["volksvertegenwoordiger.fractie.kleur"],
    volksvertegenwoordigers_df["volksvertegenwoordiger.fractie.naam"]):
    if partij not in partij_kleur_dict.keys():
        partij_kleur_dict[partij] = kleur


# In[11]:


# # Inspect results
# partij_kleur_dict


# In[12]:


#Export results to pickle file
with open(f'../data/partij_kleur_dict.pkl', 'wb') as file:
    pickle.dump(partij_kleur_dict, file)


# Then we obtain a dictionary that groups all members (and their ID) of each party, and a dictionary that maps each members and its ID to its party.

# In[13]:


# Create empty dicts
fracties_dict = {}
parlementsleden_all_dict = {}

#Iterate over all rows and store fractie, id and voornaam and naam in dicts
for index, row in volksvertegenwoordigers_df.iterrows():
    fractie = row["volksvertegenwoordiger.fractie.naam"]
    parlementslid_id = row["volksvertegenwoordiger.id"]
    voornaam_en_naam = row["volksvertegenwoordiger.voornaam"] + " " + row["volksvertegenwoordiger.naam"]
    
    if fractie not in fracties_dict:
        fracties_dict[fractie] = []
    fracties_dict[fractie].append([voornaam_en_naam, parlementslid_id])
    
    parlementsleden_all_dict[parlementslid_id] = [voornaam_en_naam, fractie]


# In[14]:


# # Inspect results
# fracties_dict
# parlementsleden_all_dict


# In[15]:


#Export results
# Save to CSV
with open(f'../data/fracties.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    for key, value in fracties_dict.items():
        writer.writerow([key, value])

with open(f'../data/parlementsleden.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    for key, value in parlementsleden_all_dict.items():
        writer.writerow([key, value])

# Save to pickle file
with open(f'../data/fracties.pkl', 'wb') as file:
    pickle.dump(fracties_dict, file)

with open(f'../data/parlementsleden.pkl', 'wb') as file:
    pickle.dump(parlementsleden_all_dict, file)


# ## Commissions

# Then we obtain the current commissions. 

# In[16]:


commissies_json = get_endpoint("/comm/huidige")

# # Inspect data
# commissies_json

# Parse json into dataframe. Visual inspection showed data is stored in 'items' key
commissies_pd = pd.DataFrame.from_dict(pd.json_normalize(commissies_json['items']), orient='columns')


# In[17]:


# # Inspect results
# commissies_pd.head()
# commissies_pd.columns
# # commissies_pd["commissie.titel"]


# In[18]:


#Only keep relevant columns
commissions_overview_df = commissies_pd[["commissie.id", "commissie.titel", "commissie.link"]]

# # Inspect results
# commissions_overview_df                                


# Then we obtain more details for each commission, using information obtained when parsing the current commissions. We store this in a dict: `commissies_samenstelling_dict`.

# In[19]:


# Parse information about each commission and store in dict
commissies_samenstelling_dict = {}

for commId in commissies_pd["commissie.id"]:
    commissies_samenstelling_dict[commId] = get_endpoint(f"/comm/{commId}")


# In[20]:


# # Inspect results
# commissies_samenstelling_dict


# Inspection of the results shows that for each commission (identified by its id), some information is provide, such as: `afkorting`, `naam`, `commissiesecretaris`, as well as `functie`. This last tag contains the various possible functions for members in the commission (such as 'voorzitter', 'vast lid', 'plaatsvervangend lid'), and the information of those members.  Hence, we can use this tag to extract the members of all commissions and store it in a dict `commission_members_dict`. We also assess which different functions occur over all commissions (see below). Based on these functions, we modify the cell below to store all relevant functions (e.g. if only 'ondervoorzitter' and 'secretary': for consistency store as 'eerste ondervoorzitter' en 'tweede ondervoorzitter').  

# In[21]:


# # Create empty dictionary to store members in
# commission_members_dict = {}

# Create empty columns in dataframe
commissions_overview_df["voorzitter"] = ""
commissions_overview_df["eerste ondervoorzitter"] = ""
commissions_overview_df["tweede ondervoorzitter"] = ""
commissions_overview_df["derde ondervoorzitter"] = ""
commissions_overview_df["vierde ondervoorzitter"] = ""
commissions_overview_df["vaste leden"] = ""
commissions_overview_df["plaatsvervangende leden"] = "" 
commissions_overview_df["toegevoegde leden"] = ""

# Create empty list to store all different functions (to later on create set of to find distinct functions)
diff_functions_list = []

# Iterate over all different commissions
for index_overview, row_overview in commissions_overview_df.iterrows():
    commissie_id = row_overview["commissie.id"]
    commissie_naam = row_overview["commissie.titel"]
    
    # Check if the commissie_id exists in commissies_samenstelling_dict (if not doing so: yields error when nan as key)
    if commissie_id in commissies_samenstelling_dict:
        # store information on members, i.e. those in tag 'functie'
        members = commissies_samenstelling_dict[commissie_id]['functie']
        
        # create empty list of names and functions for each new commission
        names = []  
        functions = []  

        # Iterate over each function / group of members
        for member_group in members:
            function_name = member_group['naam']
            # Go one level deeper to assess all members of the group / all those with this function
            for person in member_group['lid']:
                first_name = person['voornaam']
                last_name = person['naam']
                full_name = f"{first_name} {last_name}"
                parlementslid_id = person['id']

                names.append(full_name)
                functions.append(function_name)

        # Create defaultdict to group members by party, fill it, and retransfer to normal dict
        parlementsleden_groupeddict = defaultdict(list)
        for name, func in zip(names, functions):
            parlementsleden_groupeddict[func].append(name)
        parlementsleden_dict = dict(parlementsleden_groupeddict)
        
        # Append all functions to list to later on check all possible functions
        for spec_function in parlementsleden_dict.keys():
            diff_functions_list.append(spec_function) 
            
        # Fill dataframe with all members performing specific functions
        # include 'or []' to address cases where no such key found. Else, will yield None, wich cannot be concatenated with other None
        # explicitly cast to list when using 'or []' since when you use the + operator with lists, it concatenates them as expected. 
        # However, in cases where there's a single item, it might sometimes return a tuple, especially when using the or [] approach to handle None values.
        commissions_overview_df.at[index_overview, "voorzitter"] = parlementsleden_dict.get('voorzitter')
        commissions_overview_df.at[index_overview, "eerste ondervoorzitter"] = list((parlementsleden_dict.get('eerste ondervoorzitter') or []) + 
                                                                                    (parlementsleden_dict.get('ondervoorzitter') or []))
        commissions_overview_df.at[index_overview, "tweede ondervoorzitter"] = list((parlementsleden_dict.get('tweede ondervoorzitter') or []) + 
                                                                                    (parlementsleden_dict.get('secretaris') or []))
        commissions_overview_df.at[index_overview, "derde ondervoorzitter"] = list((parlementsleden_dict.get('derde ondervoorzitter') or []) + 
                                                                                   (parlementsleden_dict.get('verslaggever') or []))
        commissions_overview_df.at[index_overview, "vierde ondervoorzitter"] = parlementsleden_dict.get('vierde ondervoorzitter')
        # Add to 'vaste leden' also anyone with important functions since they are in essence 'vast lid +'.
        # Also add toegevoegd lid since they also provide information about absence. 
        commissions_overview_df.at[index_overview, "vaste leden"] = list((parlementsleden_dict.get('voorzitter') or []) +
                                                                         (parlementsleden_dict.get('eerste ondervoorzitter') or []) + 
                                                                         (parlementsleden_dict.get('ondervoorzitter') or []) + 
                                                                         (parlementsleden_dict.get('tweede ondervoorzitter') or []) + 
                                                                         (parlementsleden_dict.get('secretaris') or []) + 
                                                                         (parlementsleden_dict.get('derde ondervoorzitter') or []) +
                                                                         (parlementsleden_dict.get('verslaggever') or []) + 
                                                                         (parlementsleden_dict.get('vierde ondervoorzitter') or []) +
                                                                         (parlementsleden_dict.get('vast lid') or []) + 
                                                                         (parlementsleden_dict.get('lid') or []) + 
                                                                         (parlementsleden_dict.get('toegevoegd lid') or [])                                                                      
                                                                        )
        commissions_overview_df.at[index_overview, "plaatsvervangende leden"] = parlementsleden_dict.get('plaatsvervangend lid')
        commissions_overview_df.at[index_overview, "toegevoegde leden"] = parlementsleden_dict.get('toegevoegd lid')
#         # Assess which commissions have 'verslaggever' as function
#         # Onderzoekscommissie PFAS-PFOS apparantly has a 'verslaggever' 
#         if 'verslaggever' in parlementsleden_dict.keys():
#             print (commissie_naam)


# In[22]:


# Inspect all possible functions in various commissions
set(diff_functions_list)

# for key in commission_members_dict.keys():
#     if commission_members_dict[key][]


# In[23]:


# # # Inspect results
# # commissions_overview_df.iloc[1]['vaste leden']
# commissions_overview_df


# For some commissions, there does not seem to be much relevant information. For instance for the `Onderzoekscommissie naar de veiligheid in de kinderopvang`, `Werkgroep Institutionele Zaken` en de `Commissie ad hoc`, no permanent members or presidents are registered. Hence, those cannot be taken into account in a meaninful way to assess presence of members. Hence we can drop them out of the data frame and reset the indices. For `Controlecommissie voor Regeringsmededelingen`, no president is registered, but there are however permanent members.

# In[24]:


commissions_overview_df[(commissions_overview_df['voorzitter'].isnull()) |
                                       (commissions_overview_df['vaste leden'].apply(len) == 0)]


# In[25]:


commissions_overview_df.drop([0, 2, 24], inplace=True)
# commissions_overview_df

commissions_overview_df.reset_index(drop = True, inplace = True)
# commissions_overview_df


# ## Vergaderingen commissies

# To update the data, we need to ascertain which was the latest meeting currently registered. To do this, we load the current datafile, obtain the date of the last meeting. TheN we obtain all meetings from the day before this last meeting up until today. We start from the day before to be on the safe side, while later on removing duplicates. 

# In[26]:


# Read in current dataframe of all meetings
meetings_all_commissions_df_current = pd.read_pickle(f'../data/meetings_all_commissions_df.pkl')

# Inspect results
print("Amount of new meetings currently:", meetings_all_commissions_df_current.shape[0])

# Obtain date of last meeting
date_last_meeting = meetings_all_commissions_df_current["Datum vergadering"].max()

# Set start date one day earlier
start = date_last_meeting - timedelta(days=1)
print(f'Starting point of monitoring: {start}.')


# In[ ]:





# In[27]:


meetings_all_commissions_df_current.head()


# In[ ]:





# In[ ]:





# In[28]:


# First, we obtain the relevant time frame for which we want to obtain attendance information. If we want to assess attendance at all meetings of the current legislature, we can use the `get_endpoint()` function to obtain this.


# In[29]:


# # use endpoint to obtain information about legislaturen
# legislaturen = get_endpoint('/leg/alle')

# # Extracting the most recent legislatuur start date
# legislatuur_items = legislaturen['items']
# most_recent_legislatuur = max(legislatuur_items, key=lambda x: x['legislatuur']['start-legislatuur'])
# start_date_most_recent_legislatuur_str = most_recent_legislatuur['legislatuur']['start-legislatuur']
# start_date_most_recent_legislatuur_str

# start = datetime.strptime(start_date_most_recent_legislatuur_str, '%Y-%m-%dT%H:%M:%S%z').date()
# print(f'Starting point of monitoring: {start}.')


# In[30]:


# Set end time, (i.e. today)
end = datetime.now().date()
print(f'End point of monitoring: {end}.')


# In[31]:


# # Create string version (to append to filenames of output files)
# end_str = end.strftime("%Y-%m-%d")
# end_str


# In[32]:


# # ========================= DEVELOPMENT ==============================================
# # set temporary start time
# start = datetime(2023, 9, 1).date()
# print(f'Starting point of monitoring: {start}.')
# # ========================= DEVELOPMENT ==============================================


# Then we obtain all previous meetings for a specific commission, for a certain time frame. First, we create a helper function to extract the meeting id's of all relevant meetings (`extract_previous_meeting_ids_zoek()`). Then we use another helper function to use those meeting id's to extract the attendance information on all those meetings (`extract_meeting_details()`). 

# In[33]:


def extract_previous_meeting_ids_zoek(start_date, end_date, commission_id):
    # Convert dates to the required format (ddmmyyyy)
    start_date_str = start_date.strftime("%d%m%Y")
    end_date_str = end_date.strftime("%d%m%Y")

    # API endpoint and parameters
    endpoint = '/verg/zoek/datums'
    params = {
        'type': 'comm',  # Choosing plenaire meetings
        'datumVan': start_date_str,
        'datumTot': end_date_str,
        'idComm': commission_id  # Specific commission ID
    }

    response = requests.get(base_url + endpoint, params=params)

    if response.status_code == 200:
        # Process the response data (e.g., extract meetings)
        meetings = response.json()  # Assuming the response is in JSON format
        
        # Obtain meeting ids of all relevant meetings
        meeting_ids = [item['vergadering']['id'] for item in meetings['items']]
        
        return meeting_ids
    else:
        print(f"Failed to fetch meetings. Status code: {response.status_code}")
        return None


# In[34]:


def extract_meeting_details(idVerg:int):
    # API endpoint and parameters
    endpoint = f'/verg/{idVerg}'
    params = {
        'idVerg': idVerg  # Specific meeting ID
    }

    response = requests.get(base_url + endpoint, params=params)

    if response.status_code == 200:
        # Process the response data (e.g., extract meeting details)
        meeting_details = response.json()  # Assuming the response is in JSON format
        return meeting_details


# Then we apply both functions to obtain all attendance information for all relevant meetings for all commissions, and store them in a dict.  

# In[35]:


# Create empty column to store total of meetings for commission in relevant timeframe
commissions_overview_df["aantal vergaderingen"] = ''

# Create empty dict to store attendance information for all relevant meetings for all commissions 
overall_attendance_dict = {}

# Iterate over each commission
for index_overview, row_overview in commissions_overview_df.iterrows():
    # Obtain commission_id, commission_title and vaste leden
    commission_id = row_overview["commissie.id"]
    commission_title = row_overview["commissie.titel"]
    vaste_leden_spec_comm = row_overview["vaste leden"]
    
    #Show progress
    print("-" * 50)
    print(f"Processing: {commission_id}, {commission_title}")
    
    # For each commisison: obtain the meeting ids of the relevant previous meetings
    previous_meetings_ids = extract_previous_meeting_ids_zoek(start, end, commission_id)
    
    # Create empty dict to store information about the meetings of those meeting ids in
    aanwezigheid_vergaderingen_spec_comm_dict = {}
    
    # For each of the meeting ids: extract the meeting details, and store in dict  
    for idVerg in previous_meetings_ids:
        meeting_details = extract_meeting_details(idVerg)
        
        # Extract date of meeting (us 'datumagendering' and not e.g. 'datumbegin': if meeting cancelled: othterwise key error)
        #meeting_date = meeting_details['vergadering']['commissie'][0]['datumvan']
        meeting_date_str = meeting_details['vergadering']['datumagendering'] 
        meeting_date = datetime.strptime(meeting_date_str, "%Y-%m-%dT%H:%M:%S%z").date()
        
        #Create empty dict to store aanwezigheidsinformatie of specifieke vergadering
        aanwezigheid_spec_verg_dict = {}
        
        # Add date of meeting: convert extracted string to correct format to read as datetime object, and then only extract date()
        aanwezigheid_spec_verg_dict['Datum vergadering'] = meeting_date
        
        # Iterate over the various attendance statuses ('AANWEZIG', 'AFWEZIG', 'VERONTSCHULDIGD') 
        # Add try-except to address KeyErrors about 'aanwezigheid'
        try:    
            for attendance_status in meeting_details['vergadering']['aanwezigheid']:
                status = attendance_status['aanwezigheid-status']
                aanwezigheid_spec_verg_dict[status] = [] #Create empty list for this status to later on fill with members

                # Iterate over all people that are stored under that attendence status and obtain personal information
                for person in attendance_status['persoon']:
                    full_name = f"{person['voornaam']} {person['naam']}"
                    person_info = {
                        'Naam': full_name,
                        'id': person['id'],
                        'Fractie': person['fractie']['naam']
                    }
#                     # Store as list instead of dict to allow easier rendering in Dash
#                     person_info = [full_name, person['id'], person['fractie']['naam']]
                    # Store information in dict of spec meeting
                    aanwezigheid_spec_verg_dict[status].append(person_info)
            # Store information in attandance information dict of all relevant meetings
            aanwezigheid_vergaderingen_spec_comm_dict["Vergadering " + str(idVerg)] = aanwezigheid_spec_verg_dict
        except KeyError:
            print(f'----- No attendance information found for: idVerg: {idVerg}, meeting date: {meeting_date}')
    
        
    
    # Transform data to dataframe for easier handling
    spec_comm_df = pd.DataFrame.from_dict(aanwezigheid_vergaderingen_spec_comm_dict,
                                          orient='index') # use index orientation to get meetings as rows
    
    # Create new empty columns to contain only attendance status for permanent members
    spec_comm_df["AANWEZIG_vast"], spec_comm_df["AFWEZIG_vast"], spec_comm_df["VERONTSCHULDIGD_vast"] = "", "", ""

    # Iterate over each meeting of specific commission and assign the permanent members to the relevant attendance status in new columns
    # Use try-except to handle commissions where no column 'Afwezig' is registered
    for index_spec_comm, row_spec_comm in spec_comm_df.iterrows():
        try:
            spec_comm_df.at[index_spec_comm, "AANWEZIG_vast"] = [member for member in row_spec_comm["AANWEZIG"] if member["Naam"] in vaste_leden_spec_comm] if isinstance(row_spec_comm["AANWEZIG"], list) else []
        except: 
            spec_comm_df.at[index_spec_comm, "AANWEZIG_vast"] = None
            print(f"No column 'AANWEZIG' for {index_overview} {index_spec_comm}.")
        try: 
            spec_comm_df.at[index_spec_comm, "AFWEZIG_vast"] = [member for member in row_spec_comm["AFWEZIG"] if member["Naam"] in vaste_leden_spec_comm] if isinstance(row_spec_comm["AFWEZIG"], list) else []
        except: 
            spec_comm_df.at[index_spec_comm, "AFWEZIG_vast"] = None
            print(f"No column 'AANWEZIG' for {index_overview} {index_spec_comm}.")
        try: 
            spec_comm_df.at[index_spec_comm, "VERONTSCHULDIGD_vast"] = [member for member in row_spec_comm["VERONTSCHULDIGD"] if member["Naam"] in vaste_leden_spec_comm] if isinstance(row_spec_comm["VERONTSCHULDIGD"], list) else []
        except: 
            spec_comm_df.at[index_spec_comm, "VERONTSCHULDIGD_vast"] = None
            print(f"No column 'AANWEZIG' for {index_overview} {index_spec_comm}.")
        
    
    # Add commission name to each row, for easier filtering later on
    spec_comm_df['commissie.titel'] = commission_title
    
    # Store amount of meetings for this commission in main dataframe
    commissions_overview_df.at[index_overview, "aantal vergaderingen"] = spec_comm_df.shape[0]
    
    # Store all attendance information of all meetings of this commission in overall dict for later assessment
    overall_attendance_dict[commission_title] = spec_comm_df
    
    
    #Show progress
    print(f"+++ --> {len(overall_attendance_dict[commission_title])} meetings processed.")
print("-" * 75)
print("--> Processing complete")
print("-" * 75)


# In[36]:


# # Inspect results
# overall_attendance_dict.keys()
# overall_attendance_dict['Commissie voor Cultuur, Jeugd, Sport en Media']

# commissions_overview_df[["commissie.titel", "aantal vergaderingen"]]


# In[37]:


# Extract all meetings of all commissions, and store in dataframe
new_meetings_all_commissions_df = pd.concat([overall_attendance_dict[key] for key in overall_attendance_dict.keys()])

# Inspect results
print("Amount of new meetings since last update:", new_meetings_all_commissions_df.shape[0])

print("Amount of meetings on last day of initial data set:", 
      new_meetings_all_commissions_df[new_meetings_all_commissions_df['Datum vergadering'] == start].shape[0])
print("Amount of meetings on day before last day of initial data set (i.e. extra day):",
      new_meetings_all_commissions_df[new_meetings_all_commissions_df['Datum vergadering'] == date_last_meeting].shape[0])


# Then we merge dataframe of the old and new meeting and remove duplicates. For this, we can use the indices, as they contain the meeting id's. This is relevant since some entries are exactly identical, e.g. when 2 meetings occur on the same day with the same attendance (e.g. a full day meeting stretched over a morning and afternoon meeting). 

# In[38]:


# Concatenate the dataframes of the old meetings and the new meetings
meetings_all_commissions_df_all = pd.concat([meetings_all_commissions_df_current, 
                                             new_meetings_all_commissions_df])

# Inspect results
print("Amount of total meetings after update (incl. duplicates):", 
      meetings_all_commissions_df_all.shape[0])


# In[39]:


# Convert all values in dataframe to strings to avoid errors when using 'duplicated' feature later on (i.e. cannot work with lists) 
meetings_all_commissions_df_all_str = meetings_all_commissions_df_all.astype(str)

# Convert the index to a column (to be able to take it into account for the duplicate analysis) 
meetings_all_commissions_df_all_str['Index'] = meetings_all_commissions_df_all_str.index


# Create a boolean mask for non-duplicated items, using the transformed dataframe
mask = ~meetings_all_commissions_df_all_str.duplicated(keep='first')

# Apply the mask to the original DataFrame to filter out any duplicates
meetings_all_commissions_df = meetings_all_commissions_df_all[mask]

# Inspect results
print("Amount of total meetings after update (excl. duplicates):", 
      meetings_all_commissions_df.shape[0])


# Then we further modify the resulting dataframes. First we create some empty columns that will be later on filled during the interactive dash application. Some columns (i.e. those in `meetings_all_commissions_df` indicating how many members were present/absent/absent with notice, can however already be filled.  

# In[40]:


# Create empty columns in commissions_overview_df to fill later on using .loc
columns_to_fill = [
    'aanwezig_count_alle', 'afwezig_count_alle', 'verontschuldigd_count_alle',
    'aanwezig_count_vaste', 'afwezig_count_vaste', 'verontschuldigd_count_vaste',
    'Gemiddelde aantal aanwezig alle leden', 'Gemiddelde aantal afwezig alle leden', 
    'Gemiddelde aantal verontschuldigd alle leden',
    'Gemiddelde aantal aanwezig vaste leden', 'Gemiddelde aantal afwezig vaste leden',
    'Gemiddelde aantal verontschuldigd vaste leden']

# Assign empty strings and NaN values explicitly using .loc
for column in columns_to_fill:
    commissions_overview_df.loc[:, column] = "" if 'count' in column else np.nan


# In[41]:


# Create empty columns in meetings_all_commissions_filtered_df
new_columns = ["Aantal aanwezig alle leden", "Aantal afwezig alle leden", "Aantal verontschuldigd alle leden",
    "Aantal aanwezig vaste leden", "Aantal afwezig vaste leden", "Aantal verontschuldigd vaste leden"]

# Assign np.nan to the new columns
for new_col in new_columns:
    meetings_all_commissions_df[new_col] = np.nan

# Define a function to get the count for each column
def get_count(column):
    return len(column) if isinstance(column, list) else 0

# Modify meetings_all_commissions_filtered_df with counts for attendance statuses 
for index_spec, row_specific in meetings_all_commissions_df.iterrows():
    for column_name_spec_to_fill, column_name_to_calculate_from in zip(
        ["Aantal aanwezig alle leden", "Aantal afwezig alle leden", "Aantal verontschuldigd alle leden",
         "Aantal aanwezig vaste leden", "Aantal afwezig vaste leden", "Aantal verontschuldigd vaste leden"],
        ['AANWEZIG', 'AFWEZIG', 'VERONTSCHULDIGD','AANWEZIG_vast', 'AFWEZIG_vast', 'VERONTSCHULDIGD_vast']):
        meetings_all_commissions_df.at[index_spec, column_name_spec_to_fill] = get_count(
            meetings_all_commissions_df.loc[index_spec, column_name_to_calculate_from])


# In[43]:


# # Inspect results
# commissions_overview_df
# meetings_all_commissions_df


# In[46]:


# Extract a version of the dataframe that only contains the names of the members (i.e. the third element)
# Obtain copy of relevant dataframe
meetings_all_commissions_short_df = copy.deepcopy(meetings_all_commissions_df)
# Define the columns to modify
columns_to_modify = [col for col in ['AANWEZIG', 'AFWEZIG', 'VERONTSCHULDIGD','AANWEZIG_vast', 'AFWEZIG_vast', 'VERONTSCHULDIGD_vast']]


# Apply function to modify columns
for col in columns_to_modify:
    meetings_all_commissions_short_df[col] = meetings_all_commissions_short_df[col].apply(
        lambda x: [item["Naam"] for item in x] if isinstance(x, list) else None)


# In[45]:


# # Inspect results
# meetings_all_commissions_short_df


# Then we save the dataframes. 

# In[ ]:


# ## Save dict with all dataframes for later use
# # 1. Save as pkl. 
# with open(f'../data/vergaderingen_commissies/overall_attendance_dict_{today_str}.pkl', 'wb') as file:
#     pickle.dump(overall_attendance_dict, file)

# # 2. Save as xlsx (for easier visual inspection)
# # Create a Pandas Excel writer using xlsxwriter as the engine
# with pd.ExcelWriter(f'../data/vergaderingen_commissies/overall_attendance_dict_{today_str}.xlsx', engine='xlsxwriter') as writer:
#     # Loop through each key-value pair in the dictionary
#     for key, df in overall_attendance_dict.items():
#         # Write each DataFrame to a specific sheet in the Excel file
#         # Limit Excel worksheet name to 30 chars, else error
#         df.to_excel(writer, sheet_name=key[:31], index=False)


# In[48]:


## Save meetings_all_commissions_df for later use
# 1. Save as pkl
with open(f'../data/meetings_all_commissions_df.pkl', 'wb') as file:
    pickle.dump(meetings_all_commissions_df, file)

# 2. Save as csv
meetings_all_commissions_df.to_csv(path_or_buf = f'../data/meetings_all_commissions_df.csv',
                               sep = ";",
                               encoding = "utf-16", # to ensure trema's are well handled (e.g. Koen Daniëls)
                               index = False)


# In[49]:


# ## Save meetings_all_commissions_df for later use
# # 1. Save as pkl
# with open(f'../data/meetings_all_commissions_df_{today_str}.pkl', 'wb') as file:
#     pickle.dump(meetings_all_commissions_df, file)

# # 2. Save as csv
# meetings_all_commissions_df.to_csv(path_or_buf = f'../data/meetings_all_commissions_df_{today_str}.csv',
#                                sep = ";",
#                                encoding = "utf-16", # to ensure trema's are well handled (e.g. Koen Daniëls)
#                                index = False)


# In[50]:


## Save meetings_all_commissions_short_df for later use
# 1. Save as pkl
with open(f'../data/meetings_all_commissions_short_df.pkl', 'wb') as file:
    pickle.dump(meetings_all_commissions_short_df, file)

# 2. Save as csv
meetings_all_commissions_short_df.to_csv(path_or_buf = f'../data/meetings_all_commissions_short_df.csv',
                                         sep = ";",
                                         encoding = "utf-16", # to ensure trema's are well handled (e.g. Koen Daniëls)
                                         index = False)


# In[51]:


# ## Save meetings_all_commissions_short_df for later use
# # 1. Save as pkl
# with open(f'../data/meetings_all_commissions_short_df_{today_str}.pkl', 'wb') as file:
#     pickle.dump(meetings_all_commissions_short_df, file)

# # 2. Save as csv
# meetings_all_commissions_short_df.to_csv(path_or_buf = f'../data/meetings_all_commissions_short_df_{today_str}.csv',
#                                          sep = ";",
#                                          encoding = "utf-16", # to ensure trema's are well handled (e.g. Koen Daniëls)
#                                          index = False)


# In[52]:


## Save commissions_overview_df for later use
# 1. Save as pkl
with open(f'../data/commissions_overview_df.pkl', 'wb') as file:
    pickle.dump(commissions_overview_df, file)

# 2. Save as csv
commissions_overview_df.to_csv(path_or_buf = f'../data/commissions_overview_df.csv',
                               sep = ";",
                               encoding = "utf-16", # to ensure trema's are well handled (e.g. Koen Daniëls)
                               index = False)


# In[ ]:


# ## Save commissions_overview_df for later use
# # 1. Save as pkl
# with open(f'../data/commissions_overview_df_{today_str}.pkl', 'wb') as file:
#     pickle.dump(commissions_overview_df, file)

# # 2. Save as csv
# commissions_overview_df.to_csv(path_or_buf = f'../data/commissions_overview_df_{today_str}.csv',
#                                sep = ";",
#                                encoding = "utf-16", # to ensure trema's are well handled (e.g. Koen Daniëls)
#                                index = False)


# # Test chunks

# In[ ]:





# In[ ]:


# meetings_all_commissions_df.loc["Vergadering 1764019", "AANWEZIG_vast"][0]
# type(meetings_all_commissions_df.loc["Vergadering 1764019", "AANWEZIG_vast"][0])


# In[ ]:


# meetings_all_commissions_df["AANWEZIG_vast"].apply(
#     lambda x: [item["Naam"] for item in x] if isinstance(item, list) else None
# )


# In[ ]:





# In[ ]:





# In[ ]:


# # Convert the index to a column (to be able to take it into account for the duplicate analysis) and identify non-duplicated items
# meetings_all_commissions_df_all['Index'] = meetings_all_commissions_df_all.index
# meetings_all_commissions_df_all_str = meetings_all_commissions_df_all.astype(str)
# meetings_all_commissions_df = meetings_all_commissions_df_all_str[~meetings_all_commissions_df_all_str.duplicated(keep='first')]

# # Remove the extra column used for comparison
# meetings_all_commissions_df = meetings_all_commissions_df.drop(columns=['Index'])

# # Inspect results
# print("Amount of total meetings after update (excl. duplicates:", 
#       meetings_all_commissions_df.shape[0])


# In[ ]:


# # Convert the index to a column (to be able to take it into account for the duplicate analysis) and identify non-duplicated items
# meetings_all_commissions_df_all['Index'] = meetings_all_commissions_df_all.index
# meetings_all_commissions_df_all_str = meetings_all_commissions_df_all.astype(str)
# meetings_all_commissions_df = meetings_all_commissions_df_all_str[~meetings_all_commissions_df_all_str.duplicated(keep='first')]

# # Remove the extra column used for comparison
# meetings_all_commissions_df = meetings_all_commissions_df.drop(columns=['Index'])

# # Inspect results
# print("Amount of total meetings after update (excl. duplicates:", 
#       meetings_all_commissions_df.shape[0])


# In[ ]:





# In[ ]:


# meetings_all_commissions_df_all.index


# In[ ]:


# unique = set(meetings_all_commissions_df_all.index)
# len(unique)


# In[ ]:


# # Identify duplicates based on all columns (including the list column)
# duplicates_mask = meetings_all_commissions_df_all.apply(lambda row: tuple(row) if isinstance(row, list) else row, axis=1).duplicated(keep=False)


# # Display all items that are not unique
# non_unique_items = meetings_all_commissions_df_all[duplicates_mask]
# print(non_unique_items)


# In[ ]:





# In[ ]:





# In[ ]:


# # Convert lists to strings and identify duplicate rows based on all columns
# # Convert the index to a column and include it in the identification of duplicate rows
# meetings_all_commissions_df_all['Index'] = meetings_all_commissions_df_all.index
# df_str = meetings_all_commissions_df_all.astype(str)
# duplicate_rows = df_str[df_str.duplicated(keep=False)]

# # Display the duplicate rows
# duplicate_rows

