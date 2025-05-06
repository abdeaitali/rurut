# rail_analysis/rail_measures.py

import pandas as pd # type: ignore

def get_h_index(df, profile, gauge=None, load=None):
    """
    Extracts the H-index values for a specific rail profile and optionally a gauge.
    If gauge is not provided, returns all H-index values for the profile.

    Args:
        df (pd.DataFrame): The input DataFrame containing rail data.
        profile (str): The rail profile (e.g., 'MB5', 'MB6').
        gauge (int or str, optional): The gauge value (e.g., 1440). Defaults to None.
        load (float, optional): The load value (e.g., 30 or 32.5). Defaults to None.

    Returns:
        pd.DataFrame or None: A DataFrame of H-index values for the specified profile
                              (and gauge, if provided), indexed by 'Gauge' and 'Month'.
                              Returns None if no matching data is found.
    """
    h_index_data = df[(df['Profile'] == profile) & (df['Condition'] == 'H-index')]
    if gauge is not None:
        h_index_data = h_index_data[h_index_data['Gauge'] == gauge] # Changed from str(gauge)

    if load is not None:
        h_index_data = h_index_data[h_index_data['Load'] == load]

    if not h_index_data.empty:
        # reset index to ensure 'Gauge' and 'Month' are the new index
        h_index_data = h_index_data.reset_index(drop=True)
        return h_index_data
    else:
        return None

def get_wear_data(df, profile, gauge=None, load=None):
    """
    Extracts the wear data for a specific rail profile and optionally a gauge.
    If gauge is not provided, returns all wear data for the profile.

    Args:
        df (pd.DataFrame): The input DataFrame containing rail data.
        profile (str): The rail profile (e.g., 'MB5', 'MB6').
        gauge (int or str, optional): The gauge value (e.g., 1440). Defaults to None.
        load (float, optional): The load value (e.g., 30 or 32.5). Defaults to None.

    Returns:
        pd.DataFrame or None: A DataFrame of wear values for the specified profile
                              (and gauge, if provided), indexed by 'Gauge' and 'Month'.
                              Returns None if no matching data is found.
    """
    wear_data = df[(df['Profile'] == profile) & (df['Condition'] == 'Wear')]
    if gauge is not None:
        wear_data = wear_data[wear_data['Gauge'] == gauge] # Changed from str(gauge)

    if load is not None:
        wear_data = wear_data[wear_data['Load'] == load]

    if not wear_data.empty:
        # reset index to ensure 'Gauge' and 'Month' are the new index
        wear_data = wear_data.reset_index(drop=True)
        return wear_data
    else:
        return None

def get_rcf_residual(df, profile, gauge=None, load=None):
    """
    Extracts the residual RCF data for a specific rail profile and optionally a gauge.
    If gauge is not provided, returns all residual RCF data for the profile.

    Args:
        df (pd.DataFrame): The input DataFrame containing rail data.
        profile (str): The rail profile (e.g., 'MB5', 'MB6').
        gauge (int or str, optional): The gauge value (e.g., 1440). Defaults to None.
        load (float, optional): The load value (e.g., 30 or 32.5). Defaults to None.

    Returns:
        pd.DataFrame or None: A DataFrame of residual RCF values for the specified profile
                              (and gauge, if provided), indexed by 'Gauge' and 'Month'.
                              Returns None if no matching data is found.
    """
    rcf_residual_data = df[(df['Profile'] == profile) & (df['Condition'] == 'RCF-residual')]
    if gauge is not None:
        rcf_residual_data = rcf_residual_data[rcf_residual_data['Gauge'] == gauge] # Changed from str(gauge)

    if load is not None:
        rcf_residual_data = rcf_residual_data[rcf_residual_data['Load'] == load]

    if not rcf_residual_data.empty:
        # reset index to ensure 'Gauge' and 'Month' are the new index
        rcf_residual_data = rcf_residual_data.reset_index(drop=True)
        return rcf_residual_data
    else:
        return None

def get_rcf_depth(df, profile, gauge=None, load=None):
    """
    Extracts the RCF depth data for a specific rail profile and optionally a gauge.
    If gauge is not provided, returns all RCF depth data for the profile.

    Args:
        df (pd.DataFrame): The input DataFrame containing rail data.
        profile (str): The rail profile (e.g., 'MB5', 'MB6').
        gauge (int, optional): The gauge value (e.g., 1440). Defaults to None.
        load (float, optional): The load value (e.g., 30 or 32.5). Defaults to None.

    Returns:
        pd.DataFrame or None: A DataFrame of RCF depth values for the specified profile
                              (and gauge, if provided), indexed by 'Gauge' and 'Month'.
                              Returns None if no matching data is found.
    """
    rcf_depth_data = df[(df['Profile'] == profile) & (df['Condition'] == 'RCF-depth')]
    if gauge is not None:
        rcf_depth_data = rcf_depth_data[rcf_depth_data['Gauge'] == gauge] # Changed from str(gauge)

    if load is not None:
        rcf_depth_data = rcf_depth_data[rcf_depth_data['Load'] == load]

    if not rcf_depth_data.empty:
        # reset index to ensure 'Gauge' and 'Month' are the new index
        rcf_depth_data = rcf_depth_data.reset_index(drop=True)
        return rcf_depth_data
    else:
        return None