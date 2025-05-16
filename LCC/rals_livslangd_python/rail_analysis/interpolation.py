# rail_analysis/interpolation.py

import pandas as pd
import numpy as np
from scipy.interpolate import PchipInterpolator  # Import PchipInterpolator


def interpolate_rail_data(df, grinding_freq_max=12, condition='all', rail_profile='all', radius='all', rail='all', load='all'):
    """
    Interpolates rail data (H-index, wear, RCF) for a given condition,
    handling missing gauge values and ensuring non-negative output, using PCHIP.

    Args:
        df (pd.DataFrame): The input DataFrame containing rail data with columns
                           'Profile', 'Condition', 'Gauge', 'Month', and values.
        grinding_freq_max (int): The maximum frequency (in months) for interpolation.
        condition (str): The type of measurement to interpolate
                            ('H-index', 'Wear', 'RCF-residual', 'RCF-depth', or 'all').
        rail_profile (str, optional): The rail profile to filter by. Defaults to 'all'.
        radius (str, optional): The radius to filter by. Defaults to 'all'.
        rail (str, optional): The rail type to filter by. Defaults to 'all'.
        load (number, optional): The load to filter by. Defaults to 'all'.

    Returns:
        pd.DataFrame: A DataFrame with interpolated values, indexed by 'Gauge'.
                      Returns an empty DataFrame if no matching data is found.
    """

    # Ensure condition is lowercase and strip any extra spaces
    filtered_df = df
    if rail_profile != 'all':
        filtered_df = filtered_df[filtered_df['Profile'].str.strip().str.lower() == rail_profile.strip().lower()]
    if radius != 'all':
        filtered_df = filtered_df[filtered_df['Radius'].str.strip().str.lower() == radius.strip().lower()]
    if rail != 'all':
        filtered_df = filtered_df[filtered_df['Rail'].str.strip().str.lower() == rail.strip().lower()]
    if load != 'all':
        filtered_df = filtered_df[filtered_df['Load'] == load]

    # Filter the DataFrame based on the specified condition
    condition = condition.strip().lower()
    if condition != 'all':
        unique_conditions = [condition]
        filtered_df = filtered_df[filtered_df['Condition'].str.strip().str.lower() == condition]
    else:
        unique_conditions = filtered_df['Condition'].str.strip().str.lower().unique()

    # Interpolate data for each condition and append results
    interp_results = pd.DataFrame()
    for condition in unique_conditions:
        for profile in filtered_df['Profile'].unique():
            for radius in filtered_df['Radius'].unique():
                for load in filtered_df['Load'].unique():
                    for rail in filtered_df['Rail'].unique():
                        specific_filtered_df = filtered_df[
                            (filtered_df['Condition'].str.strip().str.lower() == condition) &
                            (filtered_df['Profile'] == profile) &
                            (filtered_df['Radius'] == radius) &
                            (filtered_df['Load'] == load) &
                            (filtered_df['Rail'] == rail)
                        ]
                        if not specific_filtered_df.empty:
                            specific_results = interpolate_condition_data(specific_filtered_df, grinding_freq_max)
                            specific_results['Rail'] = rail
                            specific_results['Load'] = load
                            specific_results['Radius'] = radius
                            specific_results['Profile'] = profile
                            specific_results['Condition'] = condition
                            interp_results = pd.concat([interp_results, specific_results], ignore_index=True)

    return interp_results


def interpolate_condition_data(filtered_df, grinding_freq_max):
    """
    Interpolates rail data for a specific condition using PCHIP.

    Args:
        filtered_df (pd.DataFrame): The filtered DataFrame containing rail data.
        condition (str): The condition to interpolate (e.g., 'H-index', 'Wear').
        grinding_freq_max (int): The maximum frequency (in months) for interpolation.

    Returns:
        list: A list of dictionaries containing interpolated results.
    """
    # Extract unique gauges and months for interpolation
    unique_gauges = filtered_df['Gauge'].unique()

    # Define the valid months for interpolation
    valid_months = np.array([0, 7, 8, 9, 10, 11, 12])

    # Create a DataFrame to store the results
    result_df = pd.DataFrame()
    
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

        # Store the results in the same format as the original filtered_df
        for month, value in enumerate(interp_values, start=1):
            row = {
            'Gauge': gauge,
            'Month': month,
            'Value': value,
            }
            # Append the row to the DataFrame
            result_df = pd.concat([result_df, pd.DataFrame([row])], ignore_index=True)

    return result_df


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def plot_heatmap(data, condition, zlabel):
    """
    Plots a 3D heatmap for the given data.

    Args:
        data (pd.DataFrame): The interpolated data to plot.
        condition (str): The condition to filter the data (e.g., 'H-index', 'Wear').
        zlabel (str): The label for the Z-axis.
    """
    # Filter the data for the given condition
    filtered_data = data[data['Condition'].str.strip().str.lower() == condition.strip().lower()]

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



def plot_all_interpolated_tables(data, radius=1465):
    """
    Plots eight figures in a single graph: two columns (Inner/Low Rail and High Rail)
    and four rows (H-index, Wear, RCF-residual, RCF-depth).

    Args:
        data (pd.DataFrame): The interpolated data to plot.
        radius (int): The radius to filter the data.
    """
    # Define the conditions and rail types
    conditions = ['h-index', 'wear', 'rcf-residual', 'rcf-depth']
    rail_types = ['inner', 'high']

    # Create a figure with subplots
    fig, axes = plt.subplots(4, 2, figsize=(8, 14), sharex=True, sharey=True)
    fig.subplots_adjust(hspace=0.3, wspace=0.2)

    for i, condition in enumerate(conditions):
        for j, rail in enumerate(rail_types):
            # Filter data for the specific condition, rail type, and radius
            filtered_data = data[
                (data['Condition'].str.strip().str.lower() == condition) &
                (data['Rail'].str.strip().str.lower() == rail) &
                (data['Radius'] == str(radius))
            ]

            if filtered_data.empty:
                axes[i, j].set_visible(False)
                continue

            # Extract unique gauges and months
            gauges = filtered_data['Gauge'].unique()
            months = filtered_data['Month'].unique()

            # Create a meshgrid for the plot
            X, Y = np.meshgrid(months, gauges)

            # Pivot the data to create a 2D array for Z values
            Z = filtered_data.pivot(index='Gauge', columns='Month', values='Value').values

            # Plot the heatmap
            ax = axes[i, j]
            surf = ax.contourf(X, Y, Z, cmap='viridis', levels=20)
            fig.colorbar(surf, ax=ax, orientation='vertical', shrink=0.8)

            # Set labels and title
            ax.set_title(f'{condition} - {rail.capitalize()}', fontsize=12)
            ax.set_xlabel('Months (since last grinding)', fontsize=10)
            ax.set_ylabel('Track gauge (mm)', fontsize=10)
    plt.show()