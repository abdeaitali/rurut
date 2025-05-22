

"""
Main script for the LCC Calculation
This module illustrates how the different functions are called to perform the Life Cycle Cost (LCC) calculations
based on the input data provided in a CSV file.
"""

# main.py

import os

from LCC.rals_livslangd_python.rail_analysis.LCC_two_rails import get_annuity_track_refactored
from LCC.rals_livslangd_python.rail_analysis.LCC_two_rails import get_annuity_track_refactored

from rail_analysis.interpolation import interpolate_rail_data
from rail_analysis.interpolation import plot_all_interpolated_tables

from rail_analysis.LCC_two_rails import get_annuity_track_refactored, plot_historical_data_two_rails

from preprocessings.read_input_data import read_input_data

import pandas as pd # type: ignore

def main():
    # Load input data
    file_path = './LCC/rals_livslangd_python/data/raw/CM2025/BDL_111_results_JL_0512_2rcfs.csv'
    try:
        # print the current working directory
        print("Current working directory:", os.getcwd())
        # Read the input data
        data_df = read_input_data(file_path)
    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
        return
    
    # interpolate the data
    data_df_interpolated = interpolate_rail_data(data_df) 

    # plot the interpolated data
    plot_all_interpolated_tables(data_df_interpolated) 

    # Example usage of the function
    grinding_freq_low = 12  # months
    grinding_freq_high = 10  # months
    gauge_freq = 48  # months



    # Perform LCC calculation
    annuity, lifetime, history = get_annuity_track_refactored(
        data_df_interpolated,
        grinding_freq_low,
        grinding_freq_high,
        gauge_freq,
        track_results=True
    )

    print(f"Annuity: {annuity:.2f} €/km/year")
    print(f"Lifetime: {lifetime:.2f} years")


    # plot the history of the results
    plot_historical_data_two_rails(history)

if __name__ == "__main__":
    main()