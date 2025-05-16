# rail_analysis/LCC.py
"""
LCC_rail.py

This module provides functions for calculating the Life Cycle Cost (LCC) and track lifetime for railway rails, considering various maintenance strategies such as grinding and tamping. It includes utilities for plotting the impact of maintenance frequencies on annuity and track lifetime, as well as visualizing historical rail condition data.

Note:
    This version contains a long, monolithic main function (`get_annuity`) that has not been refactored into smaller sub-functions. The code prioritizes clarity of the overall calculation flow over modularity.

Functions:
    - get_annuity(H_table, NW_table, maint_strategy, RCF_residual_table, RCF_depth_table, track_results=False, gauge_widening_per_year=1):
        Calculates the annuity (LCC per year) and track lifetime based on maintenance strategies and rail condition data. Optionally returns historical data for further analysis.

    - plot_annuity_and_lifetime_with_tamping(tamping_frequency, data_df, rail_profile='MB5', load=30):
        Plots the variation of annuity and track lifetime as a function of grinding frequency for a given tamping frequency.

    - plot_historical_data(historical_data):
        Visualizes the historical evolution of H-index, RCF residual, and gauge over time, and prints the resulting track lifetime in months and years.

Dependencies:
    - numpy
    - matplotlib
    - pandas
    - seaborn
    - scipy.interpolate
    - rail_analysis.rail_measures
    - rail_analysis.LCA

Global Parameters:
    Various constants for costs, technical lifetimes, and thresholds used in LCC calculations.
"""

## LCC.py


import numpy as np # type: ignore
import matplotlib.pyplot as plt # type: ignore
import pandas as pd # type: ignore
import seaborn as sns # type: ignore
from scipy.interpolate import PchipInterpolator # type: ignore

from rail_analysis.rail_measures import get_table, get_h_index, get_wear_data, get_rcf_residual, get_rcf_depth
from rail_analysis.LCA import get_LCA_renewal

# === GLOBAL PARAMETERS ===
SELECTED_PROFILE = 'MB4'  
SELECTED_GAUGE_WIDENING = 1  
SELECTED_RADIUS = '1465'

DISCOUNT_RATE = 0.04
TRACK_LENGTH_M = 1000
TECH_LIFE_YEARS = 15
MAX_MONTHS = 12 * TECH_LIFE_YEARS

CAP_POSS_PER_HOUR = 50293
TAMPING_COST_PER_M = 40
GRINDING_COST_PER_M = 50

TRACK_RENEWAL_COST = 6500 * TRACK_LENGTH_M
RAIL_RENEWAL_COST = 1500 * TRACK_LENGTH_M

POSS_GRINDING = 2
POSS_TAMPING = 5
POSS_GRINDING_TWICE = POSS_GRINDING * 5 / 3

H_MAX = 14
RCF_MAX = 0.5


# === MAIN FUNCTION ===


def get_annuity(H_table, NW_table, maint_strategy, RCF_residual_table, RCF_depth_table, track_results=False, gauge_widening_per_year=1):
    """
    Calculate the annuity (LCC per year) and track lifetime.

    Parameters:
    H_table (DataFrame): H-index table for grinding.
    NW_table (DataFrame): Natural wear table.
    maint_strategy (tuple): accumulated_maintenance_costs strategy (grinding frequency, tamping frequency).
    RCF_residual_table (DataFrame): RCF residual table.
    RCF_depth_table (DataFrame): RCF depth table.
    track_results (bool): If True, return historical data for H_curr, RCF_residual_curr, and gauge_curr.

    Returns:
    tuple: annuity (Total LCC per year), track lifetime in years, and (optional) historical data.
    """

    # Parameters
    discount_rate = 0.04  # 4%
    track_length_meter = 1000  # 1000 meters
    track_technical_lifetime_years = 15  # 15 years
    max_months = 12 * track_technical_lifetime_years

    cap_poss_per_hour = 50293  # SEK/hour
    tamping_cost_per_meter = 40  # SEK/m
    grinding_cost_per_meter = 50  # SEK/m

    track_renewal_costs = 6500 * track_length_meter + get_LCA_renewal(track_length_meter, 'Track')
    rail_renewal_cost = 1500 * track_length_meter

    poss_grinding = 2  # hours
    poss_tamping = 5  # hours
    poss_grinding_twice = poss_grinding * 5 / 3

    gauge = H_table['Gauge'].unique()
    gauge.sort()
    Xq = gauge

    H_max = 14  # Maximum H-index before end of life of the rail
    RCF_max = 0.5  # Maximum RCF residual before double grinding

    grinding_freq, tamping_freq = maint_strategy

    accumulated_maintenance_costs = 0
    accumulated_renewal_costs = track_renewal_costs
    accumulated_cap_costs = 0

    H_curr = 0
    gauge_curr = gauge[0]
    RCF_res_grinding = 0
    RCF_residual_curr = 0

    latest_grinding_since = 1
    latest_tamping_since = 1

    rail_lifetime = track_technical_lifetime_years
    #rail_lifetime_remainder = max_months

    historical_data = [] if track_results else None

    for m in range(1, max_months + 1):
        y = m / 12

        gauge_curr += gauge_widening_per_year / 12
        #rail_lifetime_remainder -= 1

        delta_H = PchipInterpolator(Xq, NW_table[NW_table['Month'] == latest_grinding_since]['Value'])(gauge_curr)

        if latest_grinding_since == grinding_freq:
            accumulated_maintenance_costs += grinding_cost_per_meter * track_length_meter / (1 + discount_rate) ** y
            latest_grinding_since = 0
            accumulated_cap_costs += poss_grinding * cap_poss_per_hour / (1 + discount_rate) ** y
            H_curr += PchipInterpolator(Xq, H_table[H_table['Month'] == grinding_freq]['Value'])(gauge_curr) - delta_H

            rcf_grinding = PchipInterpolator(Xq, RCF_residual_table[RCF_residual_table['Month'] == grinding_freq]['Value'])(gauge_curr)
            if rcf_grinding > 0:
                RCF_res_grinding += rcf_grinding
            RCF_residual_curr = RCF_res_grinding
        else:
            RCF_residual_curr = RCF_res_grinding + PchipInterpolator(Xq, RCF_depth_table[RCF_depth_table['Month'] == latest_grinding_since]['Value'])(gauge_curr)
            H_curr += delta_H

        if latest_tamping_since == tamping_freq: #or rail_lifetime_remainder == 0:
            accumulated_maintenance_costs += tamping_cost_per_meter * track_length_meter / (1 + discount_rate) ** y
            accumulated_cap_costs += poss_tamping * cap_poss_per_hour / (1 + discount_rate) ** y
            gauge_curr = gauge[0]
            latest_tamping_since = 0
            # if rail_lifetime_remainder == 0:
            #     accumulated_renewal_costs = accumulated_renewal_costs + rail_renewal_cost / (1 + discount_rate) ** y
            #     accumulated_maintenance_costs -= tamping_cost_per_meter * track_length_meter / (1 + discount_rate) ** y
            #     rail_lifetime_remainder = max_months

        if RCF_residual_curr >= RCF_max:
            RCF_residual_curr = 0
            RCF_res_grinding = 0

            grinding_cost_per_meter_twice = grinding_cost_per_meter * 5 / 3
            accumulated_maintenance_costs += grinding_cost_per_meter_twice * track_length_meter / (1 + discount_rate) ** y
            accumulated_cap_costs += poss_grinding_twice * cap_poss_per_hour / (1 + discount_rate) ** y
            delta_H_1 = PchipInterpolator(Xq, H_table[H_table['Month'] == latest_grinding_since + 1]['Value'])(gauge_curr)
            delta_H_2 = PchipInterpolator(Xq, H_table[H_table['Month'] == 1]['Value'])(gauge_curr)
            H_curr += delta_H_1 + delta_H_2
            latest_grinding_since = 0

        # if gauge_curr >= 1450:
        #     rail_lifetime_remainder = 0

        latest_grinding_since += 1
        latest_tamping_since += 1

        if H_curr > H_max:
            rail_lifetime = y
            accumulated_renewal_costs = accumulated_renewal_costs + (rail_renewal_cost+ get_LCA_renewal(track_length_meter, 'Rail')) / (1 + discount_rate) ** y
            # accumulated_renewal_costs = accumulated_renewal_costs + (rail_renewal_cost) / (1 + discount_rate) ** y
            break

        if track_results:
            historical_data.append({
                'Month': m,
                'H_curr': H_curr,
                'RCF_residual_curr': RCF_residual_curr,
                'Gauge_curr': gauge_curr
            })

    annuity = (accumulated_cap_costs + accumulated_maintenance_costs + accumulated_renewal_costs) / track_length_meter / rail_lifetime

    if track_results:
        return annuity, rail_lifetime, historical_data
    return annuity, rail_lifetime



# === PLOTTING FUNCTIONS ===


def plot_annuity_and_lifetime_with_tamping(tamping_frequency, data_df, rail_profile='MB5', load=30):
    """
    Plots the variation of annuity and track lifetime with grinding frequency for a given tamping frequency.

    Parameters:
    - tamping_frequency: Tamping frequency (in months).
    - data_df: DataFrame containing the input data.
    """


    # Define grinding frequencies
    grinding_frequencies = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

    # Initialize lists to store results
    annuity_values = []
    lifetime_values = []

    # Calculate annuity and lifetime for each grinding frequency
    for grinding_freq in grinding_frequencies:
        maint_strategy = (grinding_freq, tamping_frequency)
        annuity, rail_lifetime = get_annuity(
            get_h_index(data_df, rail_profile, load=load),
            get_wear_data(data_df, rail_profile, load=load),
            maint_strategy,
            get_rcf_residual(data_df, rail_profile, load=load),
            get_rcf_depth(data_df, rail_profile, load=load)
        )
        annuity_values.append(annuity)
        lifetime_values.append(rail_lifetime)

    # Plot the results
    fig, ax1 = plt.subplots()

    # Plot Total LCC on the left y-axis
    ax1.set_xlabel('Grinding Frequency (months)')
    ax1.set_ylabel('Annuity (SEK/m/year)', color='tab:blue')
    ax1.plot(grinding_frequencies, annuity_values, color='tab:blue', label='Total LCC')
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    # Create a second y-axis for Track Lifetime
    ax2 = ax1.twinx()
    ax2.set_ylabel('Track Lifetime (years)', color='tab:orange')
    ax2.plot(grinding_frequencies, lifetime_values, color='tab:orange', label='Track Lifetime')
    ax2.tick_params(axis='y', labelcolor='tab:orange')

    # Add a title and grid
    plt.title(f'Variation of Annuity and Track Lifetime with Grinding Frequency\n(Tamping Frequency: {tamping_frequency} months)')
    fig.tight_layout()
    plt.grid()

    # Show the plot
    plt.show()

    # Print where the minimum is reached
    min_index = np.argmin(annuity_values)
    min_grinding_freq = grinding_frequencies[min_index]
    min_annuity = annuity_values[min_index]
    min_lifetime = lifetime_values[min_index]
    print(f"Minimum annuity of {min_annuity:.2f} SEK/m/year is reached at a grinding frequency of {min_grinding_freq} months, with a track lifetime of {min_lifetime:.2f} years.")


def plot_historical_data(historical_data):
    """
    Plots the historical data for H_curr, RCF_residual_curr, and Gauge_curr over time.

    Parameters:
    - historical_data: List of dictionaries containing historical data with keys 'Month', 'H_curr', 'RCF_residual_curr', and 'Gauge_curr'.
    """

    historical_df = pd.DataFrame(historical_data)

    # figure size
    fig_size=(7, 4)

    # Plot H_curr
    plt.figure(figsize=fig_size)
    sns.lineplot(data=historical_df, x='Month', y='H_curr', marker='o')
    plt.title('Historical H_curr Values')
    plt.xlabel('Month')
    plt.ylabel('H_curr')
    plt.grid()
    plt.show()

    # Plot RCF_residual_curr
    plt.figure(figsize=fig_size)
    sns.lineplot(data=historical_df, x='Month', y='RCF_residual_curr', marker='o')
    plt.title('Historical RCF_residual_curr Values')
    plt.xlabel('Month')
    plt.ylabel('RCF_residual_curr')
    plt.grid()
    plt.show()

    # Plot Gauge_curr
    plt.figure(figsize=fig_size)
    sns.lineplot(data=historical_df, x='Month', y='Gauge_curr', marker='o')
    plt.title('Historical Gauge_curr Values')
    plt.xlabel('Month')
    plt.ylabel('Gauge_curr')
    plt.grid()
    plt.show()

    # print the lifetime in months, the last month before H_curr > H_max
    lifetime_months = historical_df['Month'].iloc[-1]
    print(f"Track lifetime in months: {lifetime_months}")
    # print the lifetime in years
    lifetime_years = lifetime_months / 12
    print(f"Track lifetime in years: {lifetime_years:.2f}")