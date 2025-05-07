from preprocessings.read_input_data import read_input_data
from rail_analysis.LCC import get_annuity
from rail_analysis.rail_measures import get_h_index, get_wear_data, get_rcf_residual, get_rcf_depth

import pandas as pd # type: ignore

"""
Main script for the LCC Calculation
This module illustrates how the different functions are called to perform the Life Cycle Cost (LCC) calculations
based on the input data provided in a CSV file.
"""

# main.py

import os

def main():
    # Load input data
    file_path = './LCC/rals_livslangd_python/data/raw/raw_data_structured_with_load.csv'
    try:
        # print the current working directory
        print("Current working directory:", os.getcwd())
        # Read the input data
        data = read_input_data(file_path)
    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
        return
    
    # Perform LCC calculation
    grinding_frequency = 12  # Example grinding frequency in months
    tamping_frequency = 12  # Example tamping frequency in months
    maint_strategy = (grinding_frequency, tamping_frequency)
    annuity, rail_lifetime = get_annuity(get_h_index(data), get_wear_data(data), maint_strategy, get_rcf_residual(data), get_rcf_depth(data))
    
    # Print results
    print("LCC Calculation Results:")
    print(annuity)
    print("Rail Lifetime:", rail_lifetime)

if __name__ == "__main__":
    main()