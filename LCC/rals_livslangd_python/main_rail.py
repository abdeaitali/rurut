"""
Main script for the LCC Calculation for a single rail
This module illustrates how the different functions are called to perform the Life Cycle Cost (LCC) calculations
based on the input data provided in a CSV file.
"""

# main.py

import os
import matplotlib.pyplot as plt
import numpy as np
from rail_analysis.LCC_single_rail import get_annuity_refactored
from rail_analysis.constants import SELECTED_GAUGE_WIDENING, TECH_LIFE_YEARS, SELECTED_RADIUS

from preprocessings.read_input_data import read_input_data

from rail_analysis.interpolation import interpolate_rail_data
from rail_analysis.interpolation import plot_all_interpolated_tables

from rail_analysis.LCC_single_rail import get_annuity_refactored
from rail_analysis.arkiv.LCC_rail_unfactored import get_annuity

from rail_analysis.rail_measures import get_h_index, get_wear_data, get_rcf_residual, get_rcf_depth, get_table



def plot_variation_annuity_lifetime(data_df_interpolated, rail='high', file_name="input.csv", export_image=False):
    """
    Loops over a range of grinding frequencies (months) with a fixed tamping frequency,
    calculates the annuity and rail lifetime using get_annuity_refactored,
    and then plots these variations. Also, annotates the optimal grinding frequency and 
    corresponding lifetime, includes the input file name (without path) in the title,
    and saves the plot to a designated folder.
    
    Parameters:
      - data_df_interpolated: The interpolated data DataFrame.
      - rail: Choose 'high' for high rail or 'inner' for low rail.
      - file_name: Name of the input data file (without path)
    """
    # Fixed tamping frequency (in months)
    tamping_freq = 48
    
    # Define a range of grinding frequencies (in months)
    grinding_freqs = list(range(1, 13))
    
    annuity_values = []
    lifetime_values = []
    
    # Loop over the defined grinding frequencies
    for grind_freq in grinding_freqs:
        maint_strategy = (grind_freq, tamping_freq)
        annuity, lifetime, _ = get_annuity_refactored(
            data_df_interpolated,
            maint_strategy,
            high_or_low_rail=rail,
            track_results=False, 
            gauge_widening_per_year=SELECTED_GAUGE_WIDENING,
            radius=SELECTED_RADIUS
        )
        annuity_values.append(annuity)
        lifetime_values.append(lifetime)
    
    # Find optimal grinding frequency (minimizes annuity)
    optimal_index = np.argmin(annuity_values)
    optimal_grinding_freq = grinding_freqs[optimal_index]
    optimal_annuity = annuity_values[optimal_index]
    optimal_lifetime = lifetime_values[optimal_index]
    
    # Plot the results using two y-axes
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    ax1.set_xlabel("Grinding Frequency (months)")
    ax1.set_ylabel("Annuity (SEK/m/year)", color="tab:blue")
    ax1.plot(grinding_freqs, annuity_values, marker="o", color="tab:blue", label="Annuity")
    ax1.tick_params(axis="y", labelcolor="tab:blue")
    ax1.grid(True)
    
    ax2 = ax1.twinx()
    ax2.set_ylabel("Rail Lifetime (years)", color="tab:orange")
    ax2.plot(grinding_freqs, lifetime_values, marker="s", linestyle="--", color="tab:orange", label="Lifetime")
    ax2.tick_params(axis="y", labelcolor="tab:orange")
    
    # Combine legends from both axes
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper center", ncol=2)
    
    # Annotate the optimal grinding frequency and lifetime on the plot
    annotation_text = f"Optimal Grinding: {optimal_grinding_freq} months\nLifetime: {optimal_lifetime:.1f} years"
    ax1.annotate(annotation_text, xy=(optimal_grinding_freq, optimal_annuity), 
                 xytext=(optimal_grinding_freq+0.5, optimal_annuity+0.05*max(annuity_values)),
                 arrowprops=dict(facecolor='black', shrink=0.05),
                 fontsize=12, bbox=dict(boxstyle="round,pad=0.3", facecolor="wheat", alpha=0.5))
    
    # Include input file name in the plot title
    plt.title(f"Variation of Annuity and Rail Lifetime\n(Input: {file_name}, Tamping = {tamping_freq} months, Rail = {rail.title()})")
    plt.tight_layout()
    
    # Save the plot
    if export_image:
        save_folder = r"C:\Users\AbdouAA\Work Folders\Documents\GitHub\rurut\LCC\rals_livslangd_python\figures\single_rail"
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)
        save_filename = f"opt_grinding_{os.path.splitext(file_name)[0]}_{rail.lower()}.png"
        save_path = os.path.join(save_folder, save_filename)
        plt.savefig(save_path)
        print(f"Plot saved to: {save_path}")
    
    plt.show()
    
    # Print optimal values
    print(f"Optimal grinding frequency for {rail} rail: {optimal_grinding_freq} months")
    print(f"Annuity for optimal grinding frequency: {optimal_annuity} SEK/m/year")
    print(f"Lifetime for optimal grinding frequency: {optimal_lifetime} years")


SELECTED_PROFILE = 'MB4'
SELECTED_LOAD = 32.5
SELECTED_GAUGE_WIDENING = 1  
SELECTED_RADIUS = '1465'
SELECTED_RAIL = 'high'


def main():
    # Load input data
    file_path = './LCC/rals_livslangd_python/data/raw/CM2025/BDL_111_results_JL_R1465.csv'
    #file_path = './LCC/rals_livslangd_python/data/raw/CM2025/BDL_111_results_JL_R495.csv'
    #file_path = './LCC/rals_livslangd_python/data/raw/mistra_result_test_R495.csv' # example from prior project
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
    grinding_freq = 5  # months
    tamping_freq = 48  # months
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
    annuity_ref, lifetime_ref, _ = get_annuity_refactored(
        data_df_interpolated,
        maint_strategy
    )

    print(f"Original get_annuity: annuity = {annuity}, lifetime = {lifetime}")
    print(f"Refactored get_annuity_refactored: annuity = {annuity_ref}, lifetime = {lifetime_ref}")


    # print that we are checking the resulting annuity and lifetime for low and high rail (using get_annuity_refactored)
    print("Checking the resulting annuity and lifetime for low and high rail...")
    # Perform LCC calculation using original function for low/inner rail
    annuity_low, lifetime_low, _= get_annuity_refactored(
        data_df_interpolated,
        maint_strategy,
        high_or_low_rail = 'inner'
    )
    # Perform LCC calculation using original function for high rail
    annuity_high, lifetime_high, _ = get_annuity_refactored(
        data_df_interpolated,
        maint_strategy,
        high_or_low_rail = 'high'
    )
    print(f"Low rail: annuity = {annuity_low}, lifetime = {lifetime_low}")
    print(f"High rail: annuity = {annuity_high}, lifetime = {lifetime_high}")

    # plot the history of the results
    #plot_historical_data(history)

    # get the name of the file without the path
    file_name = os.path.basename(file_path)

    # Call the function at the end of main() after other calculations
    plot_variation_annuity_lifetime(data_df_interpolated, rail='high', file_name=file_name, export_image=True)

if __name__ == "__main__":
    main()

