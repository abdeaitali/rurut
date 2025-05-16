# rail_analysis/rail_measures.py

import pandas as pd # type: ignore

def get_h_index(df, profile='MB4', gauge=None, load=32.5):
    """
    Extracts the H-index values for a specific rail profile and optionally a gauge.
    If gauge is not provided, returns all H-index values for the profile.

    Args:
        df (pd.DataFrame): The input DataFrame containing rail data.
        profile (str): The rail profile (e.g., 'MB5', 'MB6').
        gauge (int or str, optional): The gauge value (e.g., 1440). Defaults to None.
        load (float, optional): The load value (e.g., 30 or 32.5). Default to 32.5.

    Returns:
        pd.DataFrame or None: A DataFrame of H-index values for the specified profile
                              (and gauge, if provided), indexed by 'Gauge' and 'Month'.
                              Returns None if no matching data is found.
    """
    h_index_data = df[(df['Profile'] == profile) & (df['Condition'] == 'h-index')]
    if gauge is not None:
        h_index_data = h_index_data[h_index_data['Gauge'] == gauge] # Changed from str(gauge)

    h_index_data = h_index_data[h_index_data['Load'] == load]

    if not h_index_data.empty:
        # reset index to ensure 'Gauge' and 'Month' are the new index
        h_index_data = h_index_data.reset_index(drop=True)
        return h_index_data
    else:
        return None

def get_wear_data(df, profile='MB4', gauge=None, load=32.5):
    """
    Extracts the wear data for a specific rail profile and optionally a gauge.
    If gauge is not provided, returns all wear data for the profile.

    Args:
        df (pd.DataFrame): The input DataFrame containing rail data.
        profile (str): The rail profile (e.g., 'MB5', 'MB6').
        gauge (int or str, optional): The gauge value (e.g., 1440). Defaults to None.
        load (float, optional): The load value (e.g., 30 or 32.5). Default to 32.5.

    Returns:
        pd.DataFrame or None: A DataFrame of wear values for the specified profile
                              (and gauge, if provided), indexed by 'Gauge' and 'Month'.
                              Returns None if no matching data is found.
    """
    wear_data = df[(df['Profile'] == profile) & (df['Condition'] == 'wear')]
    if gauge is not None:
        wear_data = wear_data[wear_data['Gauge'] == gauge] # Changed from str(gauge)

    wear_data = wear_data[wear_data['Load'] == load]

    if not wear_data.empty:
        # reset index to ensure 'Gauge' and 'Month' are the new index
        wear_data = wear_data.reset_index(drop=True)
        return wear_data
    else:
        return None

def get_rcf_residual(df, profile='MB4', gauge=None, load=32.5):
    """
    Extracts the residual RCF data for a specific rail profile and optionally a gauge.
    If gauge is not provided, returns all residual RCF data for the profile.

    Args:
        df (pd.DataFrame): The input DataFrame containing rail data.
        profile (str): The rail profile (e.g., 'MB5', 'MB6').
        gauge (int or str, optional): The gauge value (e.g., 1440). Defaults to None.
        load (float, optional): The load value (e.g., 30 or 32.5). Default to 32.5.

    Returns:
        pd.DataFrame or None: A DataFrame of residual RCF values for the specified profile
                              (and gauge, if provided), indexed by 'Gauge' and 'Month'.
                              Returns None if no matching data is found.
    """
    rcf_residual_data = df[(df['Profile'] == profile) & (df['Condition'] == 'rcf-residual')]
    if gauge is not None:
        rcf_residual_data = rcf_residual_data[rcf_residual_data['Gauge'] == gauge] # Changed from str(gauge)

    rcf_residual_data = rcf_residual_data[rcf_residual_data['Load'] == load]

    if not rcf_residual_data.empty:
        # reset index to ensure 'Gauge' and 'Month' are the new index
        rcf_residual_data = rcf_residual_data.reset_index(drop=True)
        return rcf_residual_data
    else:
        return None

def get_rcf_depth(df, profile='MB4', gauge=None, load=32.5):
    """
    Extracts the RCF depth data for a specific rail profile and optionally a gauge.
    If gauge is not provided, returns all RCF depth data for the profile.

    Args:
        df (pd.DataFrame): The input DataFrame containing rail data.
        profile (str): The rail profile (e.g., 'MB5', 'MB6').
        gauge (int, optional): The gauge value (e.g., 1440). Defaults to None.
        load (float, optional): The load value (e.g., 30 or 32.5). Default to 32.5.

    Returns:
        pd.DataFrame or None: A DataFrame of RCF depth values for the specified profile
                              (and gauge, if provided), indexed by 'Gauge' and 'Month'.
                              Returns None if no matching data is found.
    """
    rcf_depth_data = df[(df['Profile'] == profile) & (df['Condition'] == 'rcf-depth')]
    if gauge is not None:
        rcf_depth_data = rcf_depth_data[rcf_depth_data['Gauge'] == gauge] # Changed from str(gauge)

    rcf_depth_data = rcf_depth_data[rcf_depth_data['Load'] == load]

    if not rcf_depth_data.empty:
        # reset index to ensure 'Gauge' and 'Month' are the new index
        rcf_depth_data = rcf_depth_data.reset_index(drop=True)
        return rcf_depth_data
    else:
        return None


def get_table(df, condition, profile='MB4', gauge=None, load=32.5, rail=None, radius=None):
    """
    Extracts data for a specific rail profile, condition, and optionally a gauge, rail, and radius.
    If gauge, rail, or radius are not provided, returns all data for the profile and condition.

    Args:
        df (pd.DataFrame): The input DataFrame containing rail data.
        condition (str): The condition to filter by (e.g., 'H-index', 'Wear', 'RCF-residual', 'RCF-depth').
        profile (str): The rail profile (e.g., 'MB5', 'MB6'). Defaults to 'MB5'.
        gauge (int or str, optional): The gauge value (e.g., 1440). Defaults to None.
        load (float, optional): The load value (e.g., 30 or 32.5). Default to 32.5.
        rail (str, optional): The rail type (e.g., 'Inner', 'High'). Defaults to None.
        radius (str, optional): The radius type (e.g., 'Tangent', '1465'). Defaults to None.

    Returns:
        pd.DataFrame or None: A DataFrame of values for the specified profile, condition
                              (and gauge, rail, radius if provided), indexed by 'Gauge' and 'Month'.
                              Returns None if no matching data is found.
    """
    filtered_data = df[
        (df['Profile'].str.strip().str.lower() == profile.strip().lower()) &
        (df['Condition'].str.strip().str.lower() == condition.strip().lower())
    ]
    if gauge is not None:
        filtered_data = filtered_data[filtered_data['Gauge'] == gauge]
    if rail is not None:
        filtered_data = filtered_data[filtered_data['Rail'].str.strip().str.lower() == rail.strip().lower()]
    if radius is not None:
        filtered_data = filtered_data[filtered_data['Radius'].str.strip().str.lower() == radius.strip().lower()]
    filtered_data = filtered_data[filtered_data['Load'] == load]

    if not filtered_data.empty:
        # reset index to ensure 'Gauge' and 'Month' are the new index
        filtered_data = filtered_data.reset_index(drop=True)
        return filtered_data
    else:
        return None

    