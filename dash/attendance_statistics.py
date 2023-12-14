from collections import Counter, defaultdict
import numpy as np
import pandas as pd

# Define function to obtain counters for the relevant dataframes
def obtain_attendance_counter(DataFrame_column_attendance):
    # Create empty list to store all names for relevant attendance status
    flattened_list_attendance = []
    
    # Iterate over all meetings and the corresponding lists for this attendance status
    for attendance_list in DataFrame_column_attendance:
        # Check if the attendance_list is NaN or not a list
        if attendance_list is not np.nan and isinstance(attendance_list, list):
            # Extract only names and extend to list (to ensure flat list)
            attendance_names = [item["Naam"] for item in attendance_list]
            flattened_list_attendance.extend(attendance_names)
     
    # Count occurrences of members for all meetings represented in attandance_list
    element_counts = Counter(flattened_list_attendance)
    
    # Sort elements by their counts in descending order
    sorted_counts = sorted(element_counts.items(), key=lambda x: x[1], reverse=True)

    return sorted_counts  

def obtain_attendance_statistics(commissions_overview_df_input, meetings_all_commissions_df_input):
    # ***************************************************************************************
    # Obtain average presence for all meetings of each commission (for both alle and vaste leden)
    # Extracting the last 6 columns
    relevant_counts_attendance = meetings_all_commissions_df_input.iloc[:, -6:]
    # Calculate average for each column
    average_relevant_counts_attendance = relevant_counts_attendance.mean()
    # ***************************************************************************************

    # Amend commissions_overview_filtered_df with overview how often each member was present / absent / verontschuldigd
    # + include averages attendances over all meetings of each commission

    # Iterate over each commission
    for index_overview, row_overview in commissions_overview_df_input.iterrows():
        # only modify dataframe with respect to commissions for which meetings were held
        if row_overview["aantal vergaderingen"] != 0:
            # Obtain commission title and its permanent members
            spec_commission_title = row_overview["commissie.titel"]

            # Select relevant meetings for this commission out of meetings_all_commissions_df_input
            # If only 1 meeting was selected, this results in the same dataframe
            meetings_all_commissions_df_input_relevant = meetings_all_commissions_df_input[
                meetings_all_commissions_df_input["commissie.titel"] == spec_commission_title]



            # Obtain how often (permanent) members were present, absent and absent with notice
            for column_name_overview, column_name_spec in zip(['aanwezig_count_alle', 'afwezig_count_alle', 'verontschuldigd_count_alle',
                                                               'aanwezig_count_vaste', 'afwezig_count_vaste', 'verontschuldigd_count_vaste'],
                                                              ['AANWEZIG', 'AFWEZIG', 'VERONTSCHULDIGD',
                                                               'AANWEZIG_vast', 'AFWEZIG_vast', 'VERONTSCHULDIGD_vast']):
                commissions_overview_df_input.at[index_overview, column_name_overview] = obtain_attendance_counter(
                    meetings_all_commissions_df_input_relevant[column_name_spec])

            # Obtain average presence for all meetings of this commission (for both alle and vaste leden)
            # Extracting the last 6 columns, i.e. where attendance counts are stored
            relevant_counts_attendance = meetings_all_commissions_df_input_relevant.iloc[:, -6:]
            # Calculate average for each column
            average_relevant_counts_attendance = relevant_counts_attendance.mean()

            # Iterate over the column names and assign the values to the DataFrame
            for i, col_name_overview in enumerate(['Gemiddelde aantal aanwezig alle leden', 'Gemiddelde aantal afwezig alle leden',
                                          'Gemiddelde aantal verontschuldigd alle leden',
                                          'Gemiddelde aantal aanwezig vaste leden', 'Gemiddelde aantal afwezig vaste leden',
                                          'Gemiddelde aantal verontschuldigd vaste leden']):
                commissions_overview_df_input.loc[index_overview, col_name_overview] = average_relevant_counts_attendance.iloc[i]
    
    
    
    return (commissions_overview_df_input)
    
    
    
    
def obtain_aggregated_counts(dataframe_column):
    """
    Create function to aggregate counts per member over all commissions, to get overall totals per member
    """
    # Create a defaultdict to store aggregated counts per member
    aggregated_counts = defaultdict(int)

    # Iterate through each row and aggregate counts per member
    for row in dataframe_column:
        for member, count in row:
            aggregated_counts[member] += count

    # Convert aggregated counts dictionary to a DataFrame
    aggregated_df = pd.DataFrame(list(aggregated_counts.items()), columns=['Member', 'Aggregated_Count'])

    aggregated_df

    # Create a defaultdict to store aggregated counts per member
    aggregated_counts = defaultdict(int)

    # Iterate through each row and aggregate counts per member
    for row in dataframe_column:
        for member, count in row:
            aggregated_counts[member] += count

    # Convert aggregated counts dictionary to a DataFrame
    aggregated_df = pd.DataFrame(list(aggregated_counts.items()), columns=['Member', 'Aggregated_Count'])
    
    # Sort the DataFrame based on Aggregated_Count in descending order
    aggregated_df = aggregated_df.sort_values(by='Aggregated_Count', ascending=False)
  
    return aggregated_df

def find_member(dictionary, member_name):
    """
    Function to add member of party to dataframe
    """
    for key, value in dictionary.items():
        for member in value:
            if member[0] == member_name:
                return key
    return None  # Return None if member is not found in any group
    

def get_overall_presence(dataframe_attendance_column, fracties_dict):
    # Initialize a defaultdict to store aggregated counts for each party
    party_counts = defaultdict(int)

    # Loop through each row of attendance counts
    for row in dataframe_attendance_column:
        # Loop through each member and their count in the row
        for member, count in row:
            # Match the member's name to their party and accumulate their count
            for party, members in fracties_dict.items():
                if any(member_name == member for member_name, _ in members):
                    party_counts[party] += count
                    break  # Stop iterating if the member is found in a party
    return dict(party_counts)