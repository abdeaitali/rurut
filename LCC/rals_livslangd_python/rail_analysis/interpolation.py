# rail_analysis/interpolation.py

import pandas as pd
import numpy as np
from scipy.interpolate import PchipInterpolator  # Import PchipInterpolator

def interpolate_rail_data(df, grinding_freq_max, measure_type, rail_profile=None):
    """
    Interpolates rail data (H-index, wear, RCF) for a given measure type,
    handling missing gauge values and ensuring non-negative output, using PCHIP.

    Args:
        df (pd.DataFrame): The input DataFrame containing rail data with columns
                           'Profile', 'Condition', 'Gauge', 'Month', and month values.
        grinding_freq_max (int): The maximum frequency (in months) for interpolation.
        measure_type (str): The type of measurement to interpolate
                            ('H-index', 'Wear', 'RCF-residual', 'RCF-depth').

    Returns:
        pd.DataFrame: A DataFrame with interpolated values, indexed by 'Gauge'.
                        Returns an empty DataFrame if no matching data is found.
    """
    # if no rail_profile is provided, use MB5 as default
    if rail_profile is None:
        rail_profile = 'MB5'

    # Ensure measure_type is lowercase and strip any extra spaces
    measure_type = measure_type.strip().lower()

    # Filter the DataFrame based on the specified measure_type
    filtered_df = df[df['Condition'].str.strip().str.lower() == measure_type]

    # filter the DataFrame based on the specified rail_profile
    filtered_df = filtered_df[filtered_df['Profile'].str.strip().str.lower() == rail_profile.strip().lower()]


    if filtered_df.empty:
        print(f"Warning: No data found for measure type: {measure_type}")
        return pd.DataFrame()  # Return an empty DataFrame

    # Extract unique gauges and months for interpolation
    unique_gauges = filtered_df['Gauge'].unique()

    # Define the valid months for interpolation
    valid_months = np.array([0, 7, 8, 9, 10, 11, 12])

    # Prepare DataFrame for results
    interp_results = []

    for gauge in unique_gauges:
        gauge_data = filtered_df[filtered_df['Gauge'] == gauge]
        if gauge_data.empty:
            continue

        # Extract the months and values for the current gauge
        gauge_months = gauge_data['Month'].values
        gauge_values = gauge_data['Value'].values

        # Ensure all valid months are included, appending 0 for missing month 0
        all_months = np.concatenate(([0], gauge_months))
        all_values = np.concatenate(([0], gauge_values))

        # Sort the months and corresponding values
        sorted_indices = np.argsort(all_months)
        all_months = all_months[sorted_indices]
        all_values = all_values[sorted_indices]

        # Filter to include only the valid months
        valid_indices = np.isin(all_months, valid_months)
        valid_months_filtered = all_months[valid_indices]
        valid_values_filtered = all_values[valid_indices]

        if len(valid_months_filtered) < 2:
            continue

        # Create the PCHIP interpolator
        pchip_interp = PchipInterpolator(valid_months_filtered, valid_values_filtered)

        # Perform the interpolation using PCHIP
        interp_values = pchip_interp(np.arange(1, grinding_freq_max + 1))
        #interp_values = np.maximum(interp_values, 0)  # Ensure non-negative values

        # Store the results in the same format as the original filtered_df
        for month, value in enumerate(interp_values, start=1):
            interp_results.append({
            'Profile': rail_profile,
            'Condition': measure_type,
            'Gauge': gauge,
            'Month': month,
            'Value': value
            })

        if not interp_results:
            return pd.DataFrame()

    interp_df = pd.DataFrame(interp_results)
    return interp_df


import matplotlib.pyplot as plt
import numpy as np

def plot_heatmap(data, condition, zlabel):
    """
    Plots a 3D heatmap for the given data.

    Args:
        data (pd.DataFrame): The interpolated data to plot.
        condition (str): The condition to filter the data (e.g., 'H-index', 'Wear').
        zlabel (str): The label for the Z-axis.
    """
    # Filter the data for the given condition
    filtered_data = data[data['Condition'] == condition]

    # Extract unique gauges and months
    gauges = filtered_data['Gauge'].unique()
    months = filtered_data['Month'].unique()

    # Create a meshgrid for the plot
    X, Y = np.meshgrid(months, gauges)

    # Pivot the data to create a 2D array for Z values
    Z = filtered_data.pivot(index='Gauge', columns='Month', values='Value').values

    # Plot the heatmap
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')
    surf = ax.plot_surface(X, Y, Z, cmap='viridis', edgecolor='none')

    ax.set_xlabel('Months (since last grinding)', fontsize=14, labelpad=10)
    ax.set_ylabel('Track gauge (mm)', fontsize=14, labelpad=10)
    ax.set_zlabel(f'{zlabel} (mm)', fontsize=14, labelpad=10)
    ax.set_title(f'Interpolated {condition} look-up table', fontsize=16)
    fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10)
    plt.show()