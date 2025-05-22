
"""
Main script for the LCC Calculation for a single rail
This module illustrates how the different functions are called to perform the Life Cycle Cost (LCC) calculations
based on the input data provided in a CSV file.
"""

# main.py

import os

from preprocessings.read_input_data import read_input_data

from rail_analysis.interpolation import interpolate_rail_data, plot_all_interpolated_tables, plot_specific_interpolated_tables

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
    file_path = './LCC/rals_livslangd_python/data/raw/CM2025/BDL_111_results_JL_R495.csv'
    #file_path = './LCC/rals_livslangd_python/data/raw/CM2025/BDL_111_results_JL_R1465.csv'
    #file_path = './LCC/rals_livslangd_python/data/raw/CM2025/BDL_111_results_JL_0512_2rcfs.csv'

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
#    plot_all_interpolated_tables(data_df_interpolated) 
    #plot_specific_interpolated_tables(data_df_interpolated, conditions=['h-index', 'wear', 'rcf-depth'])

    # Example usage of the function
    tamping_freq = 48  # months
    grinding_freq_low = 6  # months
    grinding_freq_high = 5  # months


    # print that we are checking the resulting annuity and lifetime for low and high rail (using get_annuity_refactored)
    print("Checking the resulting annuity and lifetime for low and high rail...")
    # Perform LCC calculation using original function for low/inner rail
    maint_strategy = (grinding_freq_low, tamping_freq)
    annuity_low, lifetime_low, _ = get_annuity_refactored(
        data_df_interpolated,
        maint_strategy,
        high_or_low_rail = 'inner'
    )
    # Perform LCC calculation using original function for high rail
    maint_strategy = (grinding_freq_high, tamping_freq)
    annuity_high, lifetime_high, _ = get_annuity_refactored(
        data_df_interpolated,
        maint_strategy,
        high_or_low_rail = 'high'
    )
    print(f"Low rail: annuity = {annuity_low}, lifetime = {lifetime_low}")
    print(f"High rail: annuity = {annuity_high}, lifetime = {lifetime_high}")

    annuity, rail_lifetime, _ = get_annuity_track_refactored(data_df_interpolated, grinding_freq_low, grinding_freq_high, tamping_freq, verbose=True, plot_timeline=False)
    print(f"Total LCC: {annuity:.2f} SEK/m/year")
    print(f"Rail lifetime: {rail_lifetime:.2f} years")


    # from rail_analysis.LCC_optimisation import optimise_and_compare

    # _ = optimise_and_compare(
    # data_df,
    # grinding_freq_low=10,
    # grinding_freq_high=10,
    # gauge_freq=48,
    # track_results=False,
    # bar_chart=True
    # )

if __name__ == "__main__":
    main()