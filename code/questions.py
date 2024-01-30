#!/usr/bin/env python
# coding: utf-8

# # Set up

# In[1]:


# import numpy as np
import pandas as pd

import re

# import csv
import pickle

# from collections import defaultdict

import requests

# from datetime import datetime
# import locale # to allow date parsing for dates in Dutch

# from collections import Counter

# import matplotlib.pyplot as plt

# import copy


# In[2]:


# # show all outputs of cell, not merely of last line (i.e. default of Jupyter Notebook)
# from IPython.core.interactiveshell import InteractiveShell
# InteractiveShell.ast_node_interactivity = "all"


# In[3]:


# Read in list of members and their parties to later on do mapping
with open('../data/parlementsleden.pkl', 'rb') as file:
    parlementsleden_all_dict = pickle.load(file)


# Interesting fields for questions:
# * /schv/lijst: Schriftelijke vragen op basis van id's van de vragen
# * /vi/lijst: Lijst van vragen en interpellaties op basis van id's  van de initiatieven

# # Obtain relevant id's

# First we need to obtain the id's of all relevant questions. There is no straightforward way to obtain this. Contact with the administration of the Flemish Parliament learns that the best way to do this is to launch a search query for the questions, and then use the 'opendata' tags to obtain the relevant id's of all results. 
# 
# Such a query can f.e. be the following: 'https://ws.vlpar.be/api/search/query/+inmeta:zittingsjaar=2023-2024&requiredfields=paginatype:Parlementair%20document.aggregaat:Vraag%20of%20interpellatie.initiatief:Schriftelijke%20vraag?collection=vp_collection&sort=date&max=100&page=1'. This lists all written questions ('Schriftelijke vragen') within the working year 2023-2024. However, it seems not possible to obtain all results at one go. The amount of search results that can be displayed on the first page is limited (f.e. not possible to list more than 100 results on the same page). 
# 
# Nevertheless, a count is provided. so it is possible to iterate through all pages with each 100 results to obtain all search results. 

# First, we define various functions to obtain these search results and id's. 

# It seems not possible to obtain all data for an entire parliamentary term ('zittingsperiode'). however, it is possible to iterate through various parliamentary years ('zittingsjaren'.

# In[4]:


def get_request(url_query:str):
    """
    Parse data from search query using url
    """
    # Make the GET request, specifing you want to use json as header, instead of xml
    response = requests.get(url_query, headers = {"Accept": "application/json"})

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        data = response.json()  # Parse JSON response
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")

    return data


# In[5]:


def get_written_question_details(url_query: str):
    """
    Return id's of all questions by iterating over all pages
    """
    url_page = f"{url_query}1" # Initialize page at 1
    # obtain output of first page of search results
    first_page = get_request(url_page)

    # Obtain amount of total results for query
    total = int(first_page['count'])
    print("Total amount of questions: ", total)

    # obtain amount of pages are needed to display all results 
    # (i.e. amount of full pages of 100 results + page with remainder)
    pages = total//100 + 1

    
    questions_details_list = []
    
    # Iterate over all pages, starting from page 1
    for page in range(1,pages+1):
        url_page = f"{url_query}{page}" # initialise URL based on relevant page
        data = get_request(url_page)
        
        # iterate over each question in the results, extract relevant details and store in dict
        for question in data["result"]:
            question_details_dict = {
                'id': re.search(r'\d+$', question['url']).group(),
                # analysis of the raw data and the main website indidate that 'themadatum' is the date when a question was asked, and 'statusdatumSchvBeantwoord' the date of answering. 
                'datum gesteld': next((tag['value'] for tag in question['metatags']['metatag'] if tag['name'] == 'themadatum'), None), 
                'datum beantwoord': next((tag['value'] for tag in question['metatags']['metatag'] if tag['name'] == 'statusdatumSchvBeantwoord'), None),
                'minister': next((tag['value'] for tag in question['metatags']['metatag'] if tag['name'] == 'minister'), None),
                'onderwerp': next((tag['value'] for tag in question['metatags']['metatag'] if tag['name'] == 'onderwerp'), None),
                'documenttype': next((tag['value'] for tag in question['metatags']['metatag'] if tag['name'] == 'documenttype'), None),
                'thema': next((tag['value'] for tag in question['metatags']['metatag'] if tag['name'] == 'thema'), None),
                'vraagsteller': next((tag['value'] for tag in question['metatags']['metatag'] if tag['name'] == 'vraagsteller'), None),
                # 'url': next((tag['value'] for tag in question if tag['name'] == 'url'), None),
                'url': question["url"],
            }
            # Append the dictionary to the list
            questions_details_list.append(question_details_dict)
    
    # Create a DataFrame from the list of dictionaries
    questions_details_df = pd.DataFrame(questions_details_list) 
    return questions_details_df


# Then we apply the functions to actually obtain the details for each parliamentary year.

# In[6]:


# List of 'zittingsjaar' values
zittingsjaar_values = ['2019-2020', '2020-2021', '2021-2022', '2022-2023', '2023-2024']

# Base URL template
base_url = "https://ws.vlpar.be/api/search/query/+inmeta:zittingsjaar={}&requiredfields=paginatype:Parlementair%20document.aggregaat:Vraag%20of%20interpellatie.initiatief:Schriftelijke%20vraag?collection=vp_collection&sort=date&max=100&page="

details_questions_term_list = [] # initialize list for dfs

# Iterate over 'zittingsjaar' values
for zittingsjaar in zittingsjaar_values:
    print("Zittingsjaar: ", zittingsjaar)
    # Construct the dynamic URL
    dynamic_url = base_url.format(zittingsjaar)

    # Obtain dataframe with details for each parliamentary year
    details_questions_df = get_written_question_details(dynamic_url)
    # append to list
    details_questions_term_list.append(details_questions_df)

# concatenate to single df
details_questions_term_df = pd.concat(details_questions_term_list, ignore_index=True)


# In[7]:


# Inspect results
details_questions_term_df.shape
details_questions_term_df.head()
details_questions_term_df.tail()


# Then we modify the dataframe to prepare it for easier handling by the dash application:
# 
# * Switch the first and last names of the relevant (i.e. members of parliament and ministers). This not only improves the readability but also ensures they are more easily matched with othere data structures were names are fromatted as [first name, last name].
# * Map the relevant party to each member
# * Cast the dates to the right format
# * Include a column on the time it took to answer a question

# In[8]:


# Function to switch order and remove comma
def switch_order_and_remove_comma(name):
    first_name, last_name = map(str.strip, name.split(','))
    return f'{last_name} {first_name}'


# In[9]:


# Apply the function to the 'minister' and 'vraagsteller' column
details_questions_term_df['minister'] = details_questions_term_df['minister'].apply(switch_order_and_remove_comma)
details_questions_term_df['vraagsteller'] = details_questions_term_df['vraagsteller'].apply(switch_order_and_remove_comma)


# In[10]:


# Function to map member to party
def map_member_to_party(member):
    for key, value in parlementsleden_all_dict.items():
        if value[0] == member:
            return value[1]
    return None  # Handle the case where member is not found


# In[11]:


# Map member to party
details_questions_term_df['vraagsteller_partij'] = details_questions_term_df['vraagsteller'].map(map_member_to_party)


# In[15]:


# Finally we cast the 'datum gesteld' and 'datum beantwoord' columns to a datetime format
details_questions_term_df['datum gesteld'] = pd.to_datetime(details_questions_term_df['datum gesteld'], format='%Y-%m-%d')
details_questions_term_df['datum beantwoord'] = pd.to_datetime(details_questions_term_df['datum beantwoord'], format='%Y-%m-%d')

# Obtain time difference (do this before turning to date() - see below - to avoid errors)
details_questions_term_df['termijn antwoord'] = (details_questions_term_df['datum beantwoord'] - 
                                                 details_questions_term_df['datum gesteld']
                                                ).dt.days


# In[16]:


details_questions_term_df.head()


# In[17]:


# Convert the datetime64[ns] to date() for easier handling in dash application
details_questions_term_df['datum gesteld'] = details_questions_term_df['datum gesteld'].dt.date
details_questions_term_df['datum beantwoord'] = details_questions_term_df['datum beantwoord'].dt.date


# In[18]:


## Save details_questions_term_df for later use
# 1. Save as pkl
with open('../data/details_questions_term_df.pkl', 'wb') as file:
    pickle.dump(details_questions_term_df, file)

# 2. Save as csv
details_questions_term_df.to_csv(path_or_buf = '../data/details_questions_term_df.csv',
                               sep = ";",
                               encoding = "utf-16", # to ensure trema's are well handled (e.g. Koen Daniëls)
                               index = False)


# # Dump

# In[ ]:




