
"""
Main script for the LCC Calculation for a single rail
This module illustrates how the different functions are called to perform the Life Cycle Cost (LCC) calculations
based on the input data provided in a CSV file.
"""

# main.py

import os

from preprocessings.read_input_data import read_input_data

from rail_analysis.interpolation import interpolate_rail_data
from rail_analysis.interpolation import plot_all_interpolated_tables

from rail_analysis.LCC_single_rail import get_annuity_refactored
from rail_analysis.LCC_two_rails import get_annuity_track_refactored


#from LCC.rals_livslangd_python.rail_analysis.LCC_rail_v1 import get_annuity

SELECTED_PROFILE = 'MB4'
SELECTED_LOAD = 32.5
SELECTED_GAUGE_WIDENING = 1  
SELECTED_RADIUS = '1465'
SELECTED_RAIL = 'high'

def main():
    # Load input data
    file_path = './LCC/rals_livslangd_python/data/raw/CM2025/BDL_111_results_JL_0515.csv'
    try:
        # print the current working directory
        #print("Current working directory:", os.getcwd())
        # Read the input data
        data_df = read_input_data(file_path)
    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
        return
    

    # interpolate the data
    data_df_interpolated = interpolate_rail_data(data_df) 

    # plot the interpolated data
    #plot_all_interpolated_tables(data_df_interpolated) 

    # Example usage of the function
    grinding_freq = 12  # months
    tamping_freq = 10  # months
    maint_strategy = (grinding_freq, tamping_freq)



    # print that we are checking the resulting annuity and lifetime for low and high rail (using get_annuity_refactored)
    print("Checking the resulting annuity and lifetime for low and high rail...")
    # Perform LCC calculation using original function for low/inner rail
    annuity_low, lifetime_low = get_annuity_refactored(
        data_df_interpolated,
        maint_strategy,
        high_or_low_rail = 'inner'
    )
    # Perform LCC calculation using original function for high rail
    annuity_high, lifetime_high = get_annuity_refactored(
        data_df_interpolated,
        maint_strategy,
        high_or_low_rail = 'high'
    )
    print(f"Low rail: annuity = {annuity_low}, lifetime = {lifetime_low}")
    print(f"High rail: annuity = {annuity_high}, lifetime = {lifetime_high}")


    # Example usage of the get_lcc function
    grinding_freq_low = grinding_freq  # months
    grinding_freq_high = grinding_freq  # months
    annuity, rail_lifetime = get_annuity_track_refactored(data_df_interpolated, grinding_freq_low, grinding_freq_high, tamping_freq)
    print(f"Total LCC: {annuity:.2f} SEK/m/year")

if __name__ == "__main__":
    main()