from collections import Counter
import numpy as np
import pandas as pd

# Then we go through each attendance lists for each meeting and count how often the permanent members were present. We do this by creating helper functions: 
# * `count_member_occurrence()` to count how many members were present / absent / absent with notice for each of the relevant meetings. 
# * `extract_attendance_status_members()` to create a counter object of the attendance status of members (i.e. 'AANWEZIG', 'AFWEZIG', 'VERONTSCHULDIGD', for a specific commission. 
# * `obtain_counts_presentia(dataframe_column)` to obtain averages for each commission across all meetings for which conts were registered. 

# We then add this to the dataframe showing all commissions.

def count_member_occurrence(attendance_list: list):
    '''
    Count how many members were present / absent / absent with notice for each of the relevant meetings.
    '''
    # Check if the attendance_list is empty
    if not attendance_list:
        return []  # Return an empty list if attendance_list is empty

    # Flatten the list of lists to count attendance over all meetings in the attendance list
    # Skip empty cells that seemed to appear, as this is not informative.
    flattened_attendance = [item for sublist in attendance_list for item in sublist if item != '']

    # Count occurrences of members for all meetings represented in attandance_list
    element_counts = Counter(flattened_attendance)
    
    # Sort elements by their counts in descending order
    sorted_counts = sorted(element_counts.items(), key=lambda x: x[1], reverse=True)

    return sorted_counts
    

def extract_attendance_status_members(source_column_name: str, target_column_name: str, 
                                      rel_spec_comm_df, rel_index_overview, overview_df):
    """
    Function create counter object of the attendance status of members (i.e. 'AANWEZIG', 'AFWEZIG', 'VERONTSCHULDIGD',
    for a specific commission (using its title). 
    """
    attendance_all_meetings = []
    
    for index_spec_comm, row_spec_comm in rel_spec_comm_df.iterrows():
        attendance = [member["Naam"] for member in row_spec_comm[source_column_name]] if isinstance(row_spec_comm[source_column_name], list) else [] 
        attendance_all_meetings.append(attendance)
        
    print("source_column_name: ", source_column_name) 
    print("target_column_name: ", target_column_name),
    print("rel_spec_comm_df: ", rel_spec_comm_df)
    print("rel_index_overview: ", rel_index_overview)
    print("overview_df: ", overview_df)
    print("attendance_all_meetings is", attendance_all_meetings)
    
    # Create a copy of the DataFrame to avoid SettingWithCopyWarning
    overview_df_copy = overview_df.copy()
    
    # if no specific commission is selected 
    if len(overview_df_copy) > 1:
        # Use .loc to assign values explicitly on the copy
        overview_df_copy.loc[rel_index_overview, target_column_name] = count_member_occurrence(attendance_all_meetings)
    else:
        overview_df_copy.loc[rel_index_overview, target_column_name] = count_member_occurrence(attendance_all_meetings)

    # Update the original DataFrame with the modified copy
    overview_df.update(overview_df_copy)
    


# def obtain_counts_presentia(dataframe_column):
    # """
    # Obtain averages from column with counts, e.g. [[14, 1, 0], [10, 3, 2], ...].
    # """
    
    # # Only maintain counts that were actually recorded, i.e. only when presence was actually recorded 
    # # (e.g. not for online meetings during covid: then resulting count column is only [0,0,0])
    # counts = [presentia_list for presentia_list in dataframe_column 
              # if isinstance(presentia_list, list) and presentia_list != [0,0,0]]

    # # Convert to NumPy array for easy calculations & calculate the averages for each position
    # average_presentia = np.mean(np.array(counts), axis=0)
    
    # return average_presentia
    

def obtain_attendance_statistics(commissions_overview_df, meetings_all_commissions_df):
    # Create empty columns in commissions_overview_df to fill later on using .loc
    columns_to_fill = [
        'aanwezig_count_alle', 'afwezig_count_alle', 'verontschuldigd_count_alle',
        'aanwezig_count_vaste', 'afwezig_count_vaste', 'verontschuldigd_count_vaste',
        'Gemiddelde aantal aanwezig alle leden', 'Gemiddelde aantal verontschuldigd alle leden',
        'Gemiddelde aantal afwezig alle leden', 
        'Gemiddelde aantal aanwezig vaste leden', 'Gemiddelde aantal verontschuldigd vaste leden', 'Gemiddelde aantal afwezig vaste leden'
    ]

    # Assign empty strings and NaN values explicitly using .loc
    for column in columns_to_fill:
        commissions_overview_df.loc[:, column] = '' if 'count' in column else np.nan

    # Create empty list to store modified dataframes in for each commission, to later on concatenate
    meetings_all_commissions_df_modified_list = []

    # Iterate over all commissions
    for index_overview, row_overview in commissions_overview_df.iterrows():
        # Obtain commission title and its permanent members
        spec_commission_title = row_overview["commissie.titel"]
        vaste_leden_spec = row_overview["vaste leden"]
        
        # Filter df for relevant commission
        spec_comm_df = meetings_all_commissions_df[meetings_all_commissions_df["commissie.titel"] == spec_commission_title]
        
        for commission_overview_df_column_name, spec_df_column_name in zip(
            ['aanwezig_count_alle', 'afwezig_count_alle', 'verontschuldigd_count_alle',
             'aanwezig_count_vaste', 'afwezig_count_vaste', 'verontschuldigd_count_vaste'],
            ["AANWEZIG", "AFWEZIG", "VERONTSCHULDIGD",
             "AANWEZIG_vast", "AFWEZIG_vast", "VERONTSCHULDIGD_vast"]):
            
            print("Lenght of spec_comm_df is", len(spec_comm_df))
            print("Length of commissions_overview_df is", len(commissions_overview_df))
            
            try:
                extract_attendance_status_members(source_column_name = spec_df_column_name,
                                              target_column_name = commission_overview_df_column_name,
                                              rel_spec_comm_df = spec_comm_df,
                                              rel_index_overview = index_overview,
                                              overview_df = commissions_overview_df)
            except KeyError:
                None
            
        # **************************************************       
        # Define a function to get the count for each column
        def get_count(column):
            return [len(column) if isinstance(column, list) else 0]
        
        for index_spec_comm, row_spec_comm in spec_comm_df.iterrows():
            # Columns to iterate over
            columns = ["AANWEZIG", "VERONTSCHULDIGD", "AFWEZIG", 
                       "AANWEZIG_vast", "VERONTSCHULDIGD_vast", "AFWEZIG_vast"]

            # New columns to create
            new_columns = ["Aantal aanwezig alle leden", "Aantal afwezig kennisgeving alle leden",
                "Aantal afwezig alle leden",
                "Aantal aanwezig vaste leden", "Aantal afwezig kennisgeving vaste leden",
                "Aantal afwezig vaste leden"]

            # Assign np.nan to the new columns
            for new_col in new_columns:
                spec_comm_df[new_col] = np.nan

            # Use .copy() to create an explicit copy
            spec_comm_df_copy = spec_comm_df.copy()
            
            # Iterate through columns to update counts using .loc
            for i, col in enumerate(columns):
                spec_comm_df_copy.loc[:, new_columns[i]] = spec_comm_df[col].apply(lambda x: get_count(x)[0])

            # If you want to replace NaNs in the new columns with 0
            spec_comm_df_copy[new_columns] = spec_comm_df_copy[new_columns].fillna(0)

            # Store modified dataframe in list
            meetings_all_commissions_df_modified_list.append(spec_comm_df_copy)  # Store the copied DataFrame


        # ************************************************** 
        # Obtain average presence for all meetings of each commission (for both alle and vaste leden)
        # Extracting the last 6 columns
        relevant_counts_attendance = spec_comm_df.iloc[:, -6:]

        # Calculate average for each column
        average_relevant_counts_attendance = relevant_counts_attendance.mean()
        
        # Store in commission overview
        # Define a list of column names for easy reference
        column_names = [
            'Gemiddelde aantal aanwezig alle leden',
            'Gemiddelde aantal verontschuldigd alle leden',
            'Gemiddelde aantal afwezig alle leden',
            'Gemiddelde aantal aanwezig vaste leden',
            'Gemiddelde aantal verontschuldigd vaste leden',
            'Gemiddelde aantal afwezig vaste leden'
        ]

        # Iterate over the column names and assign the values to the DataFrame
        for i, col_name in enumerate(column_names):
            commissions_overview_df.loc[index_overview, commissions_overview_df.columns[i]] = average_relevant_counts_attendance.iloc[i]

        # **************************************************
        
        # Store modified dataframe in list
        meetings_all_commissions_df_modified_list.append(spec_comm_df)

        
        # # 4.c. Write dataframe of specific commission to csv and pickle
        # spec_comm_df.to_csv(path_or_buf = f'../data/vergaderingen_commissies/{today_str}_Commissie_{str(index_overview)}.csv',
                            # sep = ";",
                            # encoding = "utf-16", # to ensure trema's are well handled (e.g. Koen Daniëls)
                            # index = False)
        # spec_comm_df.to_pickle(f'../data/vergaderingen_commissies/{today_str}_Commissie_{str(index_overview)}.pkl')
            
        
        # # Print progress
        # print(f"{index_overview} {spec_commission_title} processed.")

    # concatenate all resulting dataframes to a single dataframe
    if meetings_all_commissions_df_modified_list:
            meetings_all_commissions_df_modified = pd.concat(meetings_all_commissions_df_modified_list, ignore_index=True)
    else:
        meetings_all_commissions_df_modified = pd.DataFrame(columns=[])  # Create an empty DataFrame


    # print("spec_comm_df is", spec_comm_df)
    
    return (commissions_overview_df, meetings_all_commissions_df_modified)