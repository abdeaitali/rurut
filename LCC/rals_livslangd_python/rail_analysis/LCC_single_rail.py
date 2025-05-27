# rail_analysis/LCC.py
"""
Key Features:
-------------

Dependencies:
-------------
- numpy
- matplotlib
- pandas
- seaborn
- scipy.interpolate
- rail_analysis.rail_measures.get_table
- rail_analysis.constants (various constants)

Usage:
------
Import this module to perform LCC analysis for railways, simulate different maintenance strategies,
and visualize the impact of grinding and tamping frequencies on rail lifetime and costs.

Functions:
----------
- calculate_grinding_costs_rail: Computes grinding costs and updates rail condition.
- calculate_tamping_costs_rail: Computes tamping costs and updates gauge.
- handle_double_grinding_rail: Handles double grinding events when RCF exceeds threshold.
- handle_rail_renewal_rail: Checks and processes rail renewal based on wear.
- get_annuity_refactored: Main function to compute annuity and rail lifetime for a given strategy.
- plot_annuity_and_lifetime_with_tamping: Visualizes annuity, LCC, and lifetime vs. grinding frequency.
- plot_historical_data_single_rail: Plots historical rail condition for a single rail.
- plot_historical_data_both_rails: Plots historical rail condition for both low and high rails.

Note:
-----
This module assumes the presence of specific data structures and constants defined in the
rail_analysis package. Ensure all dependencies are installed and data is properly formatted.

This module provides a refactored implementation for rail Life Cycle Cost (LCC) analysis, 
utilizing modular helper functions to handle the logic for grinding, tamping, double grinding, 
and rail renewal. The main function computes the annuity (LCC per year) and rail lifetime 
based on maintenance strategies, using input data and constants for rail wear, grinding, 
tamping, and renewal costs. Additional plotting functions are included to visualize the 
variation of annuity, total LCC, and rail lifetime with grinding frequency, as well as 
historical evolution of key rail parameters over time.

Key features:
- Modular helper functions for grinding, tamping, double grinding, and renewal calculations.
- Main LCC calculation function supporting flexible maintenance strategies.
- Visualization utilities for annuity, LCC, rail lifetime, and historical parameter tracking.
"""

# LCC_single_rail.py
# This module includes a refactored calculation for rail Life Cycle Cost (LCC) analysis,
# using helper functions to modularize grinding, tamping, double grinding, and renewal logic.

import numpy as np # type: ignore
import matplotlib.pyplot as plt # type: ignore
import pandas as pd # type: ignore
import seaborn as sns # type: ignore
from scipy.interpolate import PchipInterpolator # type: ignore

from rail_analysis.rail_measures import get_table
from collections import OrderedDict

from rail_analysis.constants import (
    GRINDING_COST_PER_M,
    TRACK_LENGTH_M,
    DISCOUNT_RATE,
    POSS_GRINDING,
    CAP_POSS_PER_HOUR,
    TAMPING_COST_PER_M,
    POSS_TAMPING,
    INIT_GAUGE_LEVEL,
    RCF_MAX,
    POSS_GRINDING_TWICE,
    POSS_NEW_RAIL,
    H_MAX,
    RAIL_RENEWAL_COST,
    TECH_LIFE_YEARS,
    MAX_MONTHS,
    SELECTED_GAUGE_WIDENING,
    SELECTED_RADIUS,
    SELECTED_PROFILE,
    RCF_MAX,
    ANNUAL_MGT
)

# === HELPER FUNCTIONS ===

def calculate_grinding_costs_rail(grinding_freq, since, gauge, H_curr, RCF_res_grinding, H_table, NW_table, RCF_residual_table, RCF_depth_table, y, gauge_levels):
    delta_H = PchipInterpolator(gauge_levels, NW_table[NW_table['Month'] == since]['Value'])(gauge)
    grinding_cost = 0
    cap_cost = 0
    if since == grinding_freq:
        grinding_cost = GRINDING_COST_PER_M * TRACK_LENGTH_M / (1 + DISCOUNT_RATE) ** y
        cap_cost = POSS_GRINDING * CAP_POSS_PER_HOUR / (1 + DISCOUNT_RATE) ** y
        H_curr += PchipInterpolator(gauge_levels, H_table[H_table['Month'] == grinding_freq]['Value'])(gauge) - delta_H
        RCF_res_grinding += PchipInterpolator(gauge_levels, RCF_residual_table[RCF_residual_table['Month'] == grinding_freq]['Value'])(gauge)
        RCF_curr = RCF_res_grinding
        since = 0
    else:
        RCF_curr = RCF_res_grinding + PchipInterpolator(gauge_levels, RCF_depth_table[RCF_depth_table['Month'] == since]['Value'])(gauge)
        H_curr += delta_H
    return grinding_cost, cap_cost, H_curr, RCF_res_grinding, RCF_curr, since + 1

def calculate_tamping_costs_rail(tamping_freq, since, gauge, y):
    tamping_cost = 0
    cap_cost = 0
    if since == tamping_freq:
        tamping_cost = TAMPING_COST_PER_M * TRACK_LENGTH_M / (1 + DISCOUNT_RATE) ** y
        cap_cost = POSS_TAMPING * CAP_POSS_PER_HOUR / (1 + DISCOUNT_RATE) ** y
        gauge = INIT_GAUGE_LEVEL
        since = 0
    return tamping_cost, cap_cost, gauge, since + 1

def handle_double_grinding_rail(RCF_residual_curr, since, gauge, H_table, y, RCF_res_grinding, gauge_levels):
    if RCF_residual_curr >= RCF_MAX:
        RCF_residual_curr = 0
        RCF_res_grinding = 0
        grinding_cost_per_meter_twice = GRINDING_COST_PER_M * 5 / 3
        grinding_cost = grinding_cost_per_meter_twice * TRACK_LENGTH_M / (1 + DISCOUNT_RATE) ** y
        cap_cost = POSS_GRINDING_TWICE * CAP_POSS_PER_HOUR / (1 + DISCOUNT_RATE) ** y
        delta_H_1 = PchipInterpolator(gauge_levels, H_table[H_table['Month'] == since + 1]['Value'])(gauge)
        delta_H_2 = PchipInterpolator(gauge_levels, H_table[H_table['Month'] == 1]['Value'])(gauge)
        delta_H_total = delta_H_1 + delta_H_2
        since = 0
        return grinding_cost, cap_cost, delta_H_total, RCF_res_grinding, RCF_residual_curr, since + 1
    return 0, 0, 0, RCF_res_grinding, RCF_residual_curr, since

def handle_rail_renewal_rail(H_curr, y):
    if H_curr > H_MAX:
        renewal_costs = (RAIL_RENEWAL_COST + POSS_NEW_RAIL*CAP_POSS_PER_HOUR) / (1 + DISCOUNT_RATE) ** y
        return True, renewal_costs
    return False, 0

# === MAIN LCC FUNCTION (REFACTORED) ===

def get_annuity_refactored(
    data_df,
    maint_strategy,
    high_or_low_rail='High',
    track_results=False,
    gauge_widening_per_year=SELECTED_GAUGE_WIDENING,
    radius=SELECTED_RADIUS,
):
    """
    Calculate the annuity (LCC per year) and track lifetime for a single rail.
    """
    data_df_radius = data_df[data_df['Radius'] == radius]

    # --- LOAD TABLES ---
    H_table = get_table(data_df_radius, 'h-index', profile=SELECTED_PROFILE, rail=high_or_low_rail, radius=radius)
    NW_table = get_table(data_df_radius, 'wear', profile=SELECTED_PROFILE, rail=high_or_low_rail, radius=radius)
    RCF_residual_table = get_table(data_df_radius, 'rcf-residual', profile=SELECTED_PROFILE, rail=high_or_low_rail, radius=radius)
    RCF_depth_table = get_table(data_df_radius, 'rcf-depth', profile=SELECTED_PROFILE, rail=high_or_low_rail, radius=radius)

    gauge_levels = H_table['Gauge'].unique()
    gauge_levels.sort()

    grinding_freq, tamping_freq = maint_strategy

    accumulated_maintenance_costs = 0
    accumulated_renewal_costs = 0
    accumulated_cap_costs = 0

    H_curr = 0
    gauge_curr = gauge_levels[0]
    RCF_res_grinding = 0
    RCF_residual_curr = 0

    latest_grinding_since = 1
    latest_tamping_since = 1

    rail_lifetime = TECH_LIFE_YEARS

    historical_data = [] if track_results else None

    for m in range(1, MAX_MONTHS + 1):
        y = m / 12
        gauge_curr += gauge_widening_per_year / 12

        # Grinding
        grinding_cost, cap_cost, H_curr, RCF_res_grinding, RCF_residual_curr, latest_grinding_since = calculate_grinding_costs_rail(
            grinding_freq, latest_grinding_since, gauge_curr, H_curr, RCF_res_grinding,
            H_table, NW_table, RCF_residual_table, RCF_depth_table, y, gauge_levels
        )
        accumulated_maintenance_costs += grinding_cost
        accumulated_cap_costs += cap_cost

        # Tamping
        tamping_cost, cap_cost, gauge_curr, latest_tamping_since = calculate_tamping_costs_rail(
            tamping_freq, latest_tamping_since, gauge_curr, y
        )
        accumulated_maintenance_costs += tamping_cost
        accumulated_cap_costs += cap_cost

        # Double grinding if RCF exceeds max
        grinding_cost, cap_cost, delta_H, RCF_res_grinding, RCF_residual_curr, latest_grinding_since = handle_double_grinding_rail(
            RCF_residual_curr, latest_grinding_since, gauge_curr, H_table, y, RCF_res_grinding, gauge_levels
        )
        accumulated_maintenance_costs += grinding_cost
        accumulated_cap_costs += cap_cost
        H_curr += delta_H

        # Rail renewal if H-index exceeds max
        renewal_needed, renewal_costs = handle_rail_renewal_rail(H_curr, y)
        if renewal_needed:
            rail_lifetime = y
            accumulated_renewal_costs += renewal_costs 
            break

        if track_results:
            historical_data.append({
                'Month': m,
                'H_curr': H_curr,
                'RCF_residual_curr': RCF_residual_curr,
                'Gauge_curr': gauge_curr
            })

    annuity = (accumulated_cap_costs + accumulated_maintenance_costs + accumulated_renewal_costs) / TRACK_LENGTH_M / rail_lifetime

    if track_results:
        return annuity, rail_lifetime, historical_data
    return annuity, rail_lifetime, None


# === PLOTTING FUNCTIONS ===

def plot_annuity_and_lifetime_with_tamping(tamping_frequency, data_df, high_or_low_rail='High'):
    """
    Plots the variation of annuity and track lifetime with grinding frequency for a given tamping frequency.

    Parameters:
    - tamping_frequency: Tamping frequency (in months).
    - data_df: DataFrame containing the input data.
    """


    # Define grinding frequencies
    grinding_frequencies = list(range(1, 13))

    # Initialize lists to store results
    annuity_values = []
    lifetime_values = []
    lcc_values = []

    # Calculate annuity and lifetime for each grinding frequency
    for grinding_freq in grinding_frequencies:
        maint_strategy = (grinding_freq, tamping_frequency)
        annuity, rail_lifetime, _ = get_annuity_refactored(
            data_df,
            maint_strategy,
            high_or_low_rail=high_or_low_rail,
            track_results=False,
            gauge_widening_per_year=SELECTED_GAUGE_WIDENING,
            radius=SELECTED_RADIUS,
        )
        annuity_values.append(annuity)
        lifetime_values.append(rail_lifetime)
        lcc_values.append(annuity * TECH_LIFE_YEARS)  # Total LCC in SEK/m

    # set the size of the figure
    fig_size = (12, 6)
    plt.figure(figsize=fig_size)

    # Plot the results
    fig, ax1 = plt.subplots()

    # Plot annuity on the left y-axis
    ax1.set_xlabel('Grinding interval (months)')
    ax1.set_ylabel('Costs', color='tab:blue')
    ax1.plot(grinding_frequencies, annuity_values, color='tab:blue', label='Annuity (SEK/m/year)', marker='o')
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    # Plot LCC values on the left y-axis as well, with a different style
    ax1.plot(grinding_frequencies, lcc_values, color='tab:green', linestyle='--', marker='s', label='Total LCC (SEK/m)')

    # Create a second y-axis for Track Lifetime
    ax2 = ax1.twinx()
    ax2.set_ylabel('Rail Lifetime (years)', color='tab:orange')
    ax2.plot(grinding_frequencies, lifetime_values, color='tab:orange', label='Rail lifetime')
    ax2.tick_params(axis='y', labelcolor='tab:orange')

    # Add a title and grid
    plt.title(f'Variation of Annuity, Total LCC, and Rail Lifetime with Grinding Frequency\n(gauge correction: every {tamping_frequency} months)')
    fig.tight_layout()
    plt.grid()

    # Add legends for both y-axes
    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper right')

    # Show the plot
    plt.show()

    # Print where the minimum is reached
    min_index = np.argmin(annuity_values)
    min_grinding_freq = grinding_frequencies[min_index]
    min_annuity = annuity_values[min_index]
    min_lifetime = lifetime_values[min_index]
    print(f"Optimal annuity of {min_annuity:.2f} SEK/m/year is reached at a grinding frequency of {min_grinding_freq} months, with a rail lifetime of {min_lifetime:.2f} years.")


def plot_historical_data_single_rail(historical_data):
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
    plt.axhline(y=H_MAX, color='red', linestyle='--', label='H-index Max')
    plt.title('Historical H_curr Values')
    plt.xlabel('Month')
    plt.ylabel('H_curr')
    plt.legend()
    plt.grid()
    plt.show()

    # Plot RCF_residual_curr
    plt.figure(figsize=fig_size)
    sns.lineplot(data=historical_df, x='Month', y='RCF_residual_curr', marker='o')
    plt.axhline(y=RCF_MAX, color='red', linestyle='--', label='RCF Max')
    plt.title('Historical RCF_residual_curr Values')
    plt.xlabel('Month')
    plt.ylabel('RCF_residual_curr')
    plt.legend()
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


def plot_historical_data_both_rails(history_low, history_high):
    """
    Plots the historical data for H_curr, RCF_residual_curr, and Gauge_curr over time
    for both low and high rails on the same graphs.

    Parameters:
    - history_low: List of dicts for the low rail (keys: 'Month', 'H_curr', 'RCF_residual_curr', 'Gauge_curr')
    - history_high: List of dicts for the high rail (same keys)
    """
    df_low = pd.DataFrame(history_low)
    df_high = pd.DataFrame(history_high)
    fig_size = (12, 3)

    # Set font size globally for all plots
    plt.rcParams.update({'font.size': 14})

    # Create a figure with two subplots (one above the other)
    fig, axes = plt.subplots(2, 1, figsize=(fig_size[0], fig_size[1]*2), sharex=True)

    # Plot H_curr on the first subplot
    sns.lineplot(ax=axes[0], data=df_high, x='Month', y='H_curr', marker='o', label='High rail')
    sns.lineplot(ax=axes[0], data=df_low, x='Month', y='H_curr', marker='o', label='Low rail')
    axes[0].axhline(y=H_MAX, color='red', linestyle='--', label='H-index Max (14 mm)')
    #axes[0].set_title('H-index values over the lifetime of the high & low rail')
    axes[0].set_ylabel('H-index (in mm)')
    axes[0].grid()

    # Plot RCF_residual_curr on the second subplot
    sns.lineplot(ax=axes[1], data=df_high, x='Month', y='RCF_residual_curr', marker='o', label='High rail')
    sns.lineplot(ax=axes[1], data=df_low, x='Month', y='RCF_residual_curr', marker='o', label='Low rail')
    axes[1].axhline(y=RCF_MAX, color='red', linestyle='--', label='RCF Max (0.5 mm)')
    #axes[1].set_title('RCF value over the lifetime of the high & low rail')
    axes[1].set_xlabel('Month')
    # Add a secondary x-axis showing cumulative MGT
    def months_to_mgt(months):
        return months * ANNUAL_MGT / 12
    secax = axes[1].secondary_xaxis('top', functions=(months_to_mgt, lambda mgt: mgt * 12 / ANNUAL_MGT))
    secax.set_xlabel('Traffic load (in million gross tonnes)')
    axes[1].set_ylabel('RCF value (in mm)')
    axes[1].grid()

    # Combine legends from both subplots and show only once
    handles, labels = [], []
    for ax in axes:
        h, l = ax.get_legend_handles_labels()
        handles += h
        labels += l
        ax.legend_.remove() if ax.get_legend() else None
    # Remove duplicates
    by_label = OrderedDict(zip(labels, handles))
    fig.legend(by_label.values(), by_label.keys(), loc='upper center', ncol=4, bbox_to_anchor=(0.5, 1.02), fontsize=13)

    plt.tight_layout(rect=[0, 0, 1, 0.97])
    plt.show()

    # Plot Gauge_curr
    plt.figure(figsize=fig_size)
    sns.lineplot(data=df_high, x='Month', y='Gauge_curr', marker='o', label='High rail')
    sns.lineplot(data=df_low, x='Month', y='Gauge_curr', marker='o', label='Low rail')
    plt.title('Track gauge over the lifetime of the rails')
    plt.xlabel('Month')
    plt.ylabel('Track gauge (in mm)')
    plt.legend(fontsize=13)
    plt.grid()
    plt.show()