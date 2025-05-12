import os
import pandas as pd

def get_LCA_renewal(track_length, asset_type, SHARE_ELECTRICITY=0.5, YEARS=0):
    """
    Calculate the Life Cycle Assessment (LCA) renewal costs for a specific asset type, including environmental costs.

    Parameters:
    - track_length (float): Length of the track in meters.
    - asset_type (str): Type of the asset (e.g., 'Rail', 'Track').
    - SHARE_ELECTRICITY (float, optional): Share of electricity used in the process (default is 0.5).
    - YEARS (int, optional): Number of years for the assessment (default is 0).

    Returns:
    - float: Total LCA renewal cost for the specified asset type and track length.
    """

    # print current directory
    #print("Current working directory:", os.getcwd())

    # read LCA data from a CSV file
    lca_data = pd.read_csv('../data/raw/LCA/LCA_indata.csv', delimiter=';', encoding='utf-8')
    # replace ',' with '.' in the 'Costs' column
    lca_data['Costs'] = lca_data['Costs'].str.replace(',', '.').astype(float)


    # Calculate the total renewal costs
    total_LCA_cost = lca_data[lca_data['Asset'] == asset_type]['Costs'] * track_length

    # return only the value
    total_LCA_cost = total_LCA_cost.values[0]
    return total_LCA_cost