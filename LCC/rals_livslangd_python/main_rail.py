
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

from rail_analysis.LCC_rail_v1 import get_annuity_refactored
from rail_analysis.LCC_rail import get_annuity

from rail_analysis.rail_measures import get_h_index, get_wear_data, get_rcf_residual, get_rcf_depth, get_table


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

    # get each table for a specific rail and load to study using the appropriate condition
    # Example: rail='high', radius=300

    h_index = get_table(
        data_df_interpolated,
        condition='h-index',
        rail=SELECTED_RAIL,
        radius=SELECTED_RADIUS
    )
    wear = get_table(
        data_df_interpolated,
        condition='wear',
        rail=SELECTED_RAIL,
        radius=SELECTED_RADIUS
    )

    rcf_residual = get_table(
        data_df_interpolated,
        condition='rcf-residual',
        rail=SELECTED_RAIL,
        radius=SELECTED_RADIUS
    )

    rcf_depth = get_table(
        data_df_interpolated,
        condition='rcf-depth',
        rail=SELECTED_RAIL,
        radius=SELECTED_RADIUS
    )

    # Example usage of the function
    grinding_freq = 12  # months
    tamping_freq = 10  # months
    maint_strategy = (grinding_freq, tamping_freq)


    # print that we are checking if the two function gives the same result
    print("Checking if the two functions give the same result...")
    # Perform LCC calculation using original function
    annuity, lifetime = get_annuity(
        h_index,
        wear,
        maint_strategy,
        rcf_residual,
        rcf_depth
    )

    # Perform LCC calculation using refactored function
    annuity_ref, lifetime_ref = get_annuity_refactored(
        data_df_interpolated,
        maint_strategy
    )

    print(f"Original get_annuity: annuity = {annuity}, lifetime = {lifetime}")
    print(f"Refactored get_annuity_refactored: annuity = {annuity_ref}, lifetime = {lifetime_ref}")


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

    # plot the history of the results
    #plot_historical_data(history)

if __name__ == "__main__":
    main()